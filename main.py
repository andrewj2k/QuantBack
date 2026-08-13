from copy import deepcopy

from analytics.report import printStats, saveRun
from config.configLoader import loadConfig
from engine.btEngine import BtEngine
from engine.dataFeed import DataFeed
from engine.exec import Exec
from engine.perf import PerfEval
from engine.portfolio import Portfolio
from strats.dummyStrat import DummyStrat
from strats.pairStrat import PairStrat
from strats.relCloseStrat import RelCloseStrat


def buildStrat(stratCfg):
    stratName = stratCfg["name"]
    params = stratCfg.get("params", {})

    if stratName == "dummy":
        return DummyStrat(**params)
    if stratName == "relClose":
        return RelCloseStrat(**params)
    if stratName == "pair":
        return PairStrat(**params)

    raise ValueError(f"Unsupported strategy: {stratName}")


def runBacktest(cfg, saveOutputs=True, printSummary=True):
    dataFeed = DataFeed(
        source=cfg["data"]["source"],
        symbols=cfg["data"]["symbols"],
        startDate=cfg["backtest"]["startDate"],
        endDate=cfg["backtest"]["endDate"],
    )
    strat = buildStrat(cfg["strat"])
    exec = Exec(
        slipBps=cfg["exec"]["slipBps"],
        feePerOrder=cfg["exec"]["feePerOrder"],
    )
    portfolio = Portfolio(
        cfg["portfolio"]["initCash"],
        maxPkgFrac=cfg["portfolio"]["maxPkgFrac"],
        maxDollarPerLeg=cfg["portfolio"]["maxDollarPerLeg"],
    )
    perfEval = PerfEval()

    engine = BtEngine(
        dataFeed=dataFeed,
        strat=strat,
        exec=exec,
        portfolio=portfolio,
        perfEval=perfEval,
    )
    results = engine.run()

    if saveOutputs:
        saveRun(
            results,
            equityPath=cfg["output"]["equityCurveCsv"],
            tradesPath=cfg["output"]["tradeLogCsv"],
            signalPath=cfg["output"].get("signalLogCsv"),
        )
    if printSummary:
        printStats(results["metrics"])

    return results


def withOverrides(cfg, startDate=None, endDate=None, stratParams=None):
    nextCfg = deepcopy(cfg)
    if startDate is not None:
        nextCfg["backtest"]["startDate"] = startDate
    if endDate is not None:
        nextCfg["backtest"]["endDate"] = endDate
    if stratParams:
        nextCfg["strat"]["params"].update(stratParams)
    return nextCfg


def main():
    cfg = loadConfig()
    runBacktest(cfg)


if __name__ == "__main__":
    main()
