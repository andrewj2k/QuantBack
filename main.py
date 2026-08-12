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


def main():
    cfg = loadConfig()

    dataFeed = DataFeed(
        source=cfg["data"]["source"],
        symbols=cfg["data"]["symbols"],
        startDate=cfg["backtest"]["startDate"],
        endDate=cfg["backtest"]["endDate"],
    )
    strat = buildStrat(cfg["strat"])
    exec = Exec()
    portfolio = Portfolio(cfg["portfolio"]["initCash"])
    perfEval = PerfEval()

    engine = BtEngine(
        dataFeed=dataFeed,
        strat=strat,
        exec=exec,
        portfolio=portfolio,
        perfEval=perfEval,
    )
    results = engine.run()

    saveRun(
        results,
        equityPath=cfg["output"]["equityCurveCsv"],
        tradesPath=cfg["output"]["tradeLogCsv"],
    )
    printStats(results["metrics"])


if __name__ == "__main__":
    main()
