# src/core/scenario_runner.py
from __future__ import annotations

import asyncio
import importlib
import inspect
from typing import Any

from src.core.scenario_adapter import ScenarioAdapter
from src.utils.logger import logger


class ScenarioRunner:
    @staticmethod
    def run(scenario_name: str, mode: str) -> None:
        module_path = f"Simulasyon.{scenario_name}.scenario"
        logger.info(f"[ScenarioRunner] Import: {module_path}")

        scenario_module = importlib.import_module(module_path)

        # CP_ID varsa kullan (emin senaryosunda var), yoksa senaryo adıyla türet
        cp_id = getattr(scenario_module, "CP_ID", None) or f"CP_{scenario_name.upper()}"

        adapter = ScenarioAdapter(
            scenario_name=scenario_name,
            cp_id=cp_id,
            mode=mode, # Etiketleme için mod bilgisini aktar
        )

        if not hasattr(scenario_module, "run_scenario"):
            raise RuntimeError(
                f"{module_path} içinde run_scenario() bulunamadı."
            )

        fn = getattr(scenario_module, "run_scenario")

        # İmza kontrolü: run_scenario(mode, adapter) mı? yoksa legacy mi?
        sig = inspect.signature(fn)
        params = list(sig.parameters.keys())

        result: Any
        if len(params) >= 2:
            logger.info("[ScenarioRunner] Adapter-enabled run_scenario(mode, adapter) çağrılıyor")
            result = fn(mode, adapter)
        else:
            logger.warning(
                "[ScenarioRunner] Legacy run_scenario(mode) çağrılıyor. "
                "Bu senaryo adapter kullanmıyor; event/alarm üretimi garanti değil."
            )
            result = fn(mode)

        # async döndüyse çalıştır
        if asyncio.iscoroutine(result):
            asyncio.run(result)

