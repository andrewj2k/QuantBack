#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <cmath>
#include <stdexcept>
#include <vector>

namespace {

std::vector<double> seqToVec(PyObject* seqObj) {
    PyObject* seq = PySequence_Fast(seqObj, "expected a sequence");
    if (seq == nullptr) {
        throw std::runtime_error("expected a sequence");
    }

    Py_ssize_t size = PySequence_Fast_GET_SIZE(seq);
    PyObject** items = PySequence_Fast_ITEMS(seq);
    std::vector<double> values;
    values.reserve(static_cast<size_t>(size));

    for (Py_ssize_t i = 0; i < size; ++i) {
        double value = PyFloat_AsDouble(items[i]);
        if (PyErr_Occurred()) {
            Py_DECREF(seq);
            throw std::runtime_error("sequence must contain numbers");
        }
        values.push_back(value);
    }

    Py_DECREF(seq);
    return values;
}

PyObject* calcBeta(PyObject*, PyObject* args) {
    PyObject* xsObj;
    PyObject* ysObj;
    if (!PyArg_ParseTuple(args, "OO", &xsObj, &ysObj)) {
        return nullptr;
    }

    try {
        std::vector<double> xs = seqToVec(xsObj);
        std::vector<double> ys = seqToVec(ysObj);
        if (xs.size() < 2 || xs.size() != ys.size()) {
            return PyFloat_FromDouble(1.0);
        }

        double sumX = 0.0;
        double sumY = 0.0;
        for (size_t i = 0; i < xs.size(); ++i) {
            sumX += xs[i];
            sumY += ys[i];
        }

        double meanX = sumX / static_cast<double>(xs.size());
        double meanY = sumY / static_cast<double>(ys.size());
        double varX = 0.0;
        double covXY = 0.0;
        for (size_t i = 0; i < xs.size(); ++i) {
            double dx = xs[i] - meanX;
            double dy = ys[i] - meanY;
            varX += dx * dx;
            covXY += dx * dy;
        }

        varX /= static_cast<double>(xs.size());
        covXY /= static_cast<double>(xs.size());
        if (varX == 0.0) {
            return PyFloat_FromDouble(1.0);
        }

        return PyFloat_FromDouble(covXY / varX);
    } catch (const std::exception& exc) {
        PyErr_SetString(PyExc_TypeError, exc.what());
        return nullptr;
    }
}

PyObject* rollZScore(PyObject*, PyObject* args) {
    PyObject* valuesObj;
    if (!PyArg_ParseTuple(args, "O", &valuesObj)) {
        return nullptr;
    }

    try {
        std::vector<double> values = seqToVec(valuesObj);
        if (values.empty()) {
            return Py_BuildValue("(ddd)", 0.0, 0.0, 0.0);
        }

        double sum = 0.0;
        for (double value : values) {
            sum += value;
        }
        double avg = sum / static_cast<double>(values.size());

        double sqSum = 0.0;
        for (double value : values) {
            double diff = value - avg;
            sqSum += diff * diff;
        }
        double std = std::sqrt(sqSum / static_cast<double>(values.size()));
        if (std == 0.0) {
            return Py_BuildValue("(ddd)", avg, std, 0.0);
        }

        double zScore = (values.back() - avg) / std;
        return Py_BuildValue("(ddd)", avg, std, zScore);
    } catch (const std::exception& exc) {
        PyErr_SetString(PyExc_TypeError, exc.what());
        return nullptr;
    }
}

PyObject* calcWindowStats(PyObject*, PyObject* args) {
    PyObject* logAObj;
    PyObject* logBObj;
    double hedgeRatio;
    if (!PyArg_ParseTuple(args, "OOd", &logAObj, &logBObj, &hedgeRatio)) {
        return nullptr;
    }

    try {
        std::vector<double> logA = seqToVec(logAObj);
        std::vector<double> logB = seqToVec(logBObj);
        if (logA.empty() || logA.size() != logB.size()) {
            return Py_BuildValue("(dddd)", 0.0, 0.0, 0.0, 0.0);
        }

        double spreadSum = 0.0;
        std::vector<double> spreads;
        spreads.reserve(logA.size());
        for (size_t i = 0; i < logA.size(); ++i) {
            double spread = logA[i] - hedgeRatio * logB[i];
            spreads.push_back(spread);
            spreadSum += spread;
        }

        double avg = spreadSum / static_cast<double>(spreads.size());
        double sqSum = 0.0;
        for (double spread : spreads) {
            double diff = spread - avg;
            sqSum += diff * diff;
        }

        double std = std::sqrt(sqSum / static_cast<double>(spreads.size()));
        double latestSpread = spreads.back();
        if (std == 0.0) {
            return Py_BuildValue("(dddd)", latestSpread, avg, std, 0.0);
        }

        double zScore = (latestSpread - avg) / std;
        return Py_BuildValue("(dddd)", latestSpread, avg, std, zScore);
    } catch (const std::exception& exc) {
        PyErr_SetString(PyExc_TypeError, exc.what());
        return nullptr;
    }
}

PyObject* calcSpreadWindowStats(PyObject*, PyObject* args) {
    PyObject* spreadsObj;
    if (!PyArg_ParseTuple(args, "O", &spreadsObj)) {
        return nullptr;
    }

    try {
        std::vector<double> spreads = seqToVec(spreadsObj);
        if (spreads.empty()) {
            return Py_BuildValue("(dddd)", 0.0, 0.0, 0.0, 0.0);
        }

        double sum = 0.0;
        for (double spread : spreads) {
            sum += spread;
        }
        double avg = sum / static_cast<double>(spreads.size());

        double sqSum = 0.0;
        for (double spread : spreads) {
            double diff = spread - avg;
            sqSum += diff * diff;
        }

        double std = std::sqrt(sqSum / static_cast<double>(spreads.size()));
        double latestSpread = spreads.back();
        if (std == 0.0) {
            return Py_BuildValue("(dddd)", latestSpread, avg, std, 0.0);
        }

        double zScore = (latestSpread - avg) / std;
        return Py_BuildValue("(dddd)", latestSpread, avg, std, zScore);
    } catch (const std::exception& exc) {
        PyErr_SetString(PyExc_TypeError, exc.what());
        return nullptr;
    }
}

PyMethodDef methods[] = {
    {"calc_beta", calcBeta, METH_VARARGS, "Compute a static hedge ratio."},
    {"roll_zscore", rollZScore, METH_VARARGS, "Compute rolling mean, std, and z-score."},
    {"calc_window_stats", calcWindowStats, METH_VARARGS, "Compute spread window stats in one pass."},
    {"calc_spread_window_stats", calcSpreadWindowStats, METH_VARARGS, "Compute spread-only window stats."},
    {nullptr, nullptr, 0, nullptr},
};

PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "fastStatsCpp",
    "Compiled math helpers for pair trading stats.",
    -1,
    methods,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
};

}  // namespace

PyMODINIT_FUNC PyInit_fastStatsCpp(void) {
    return PyModule_Create(&module);
}
