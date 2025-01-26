from contextlib import nullcontext
from logging import getLogger

from cpn_core.get_data.base import BaseGetDataEngine
from cpn_core.get_data.check_phat_nguoi import CheckPhatNguoiEngine
from cpn_core.get_data.csgt import CsgtEngine
from cpn_core.get_data.etraffic import EtrafficEngine
from cpn_core.get_data.phat_nguoi import PhatNguoiEngine
from cpn_core.get_data.zm_io import ZmioEngine
from cpn_core.models.plate_info import PlateInfo
from cpn_core.models.violation_detail import ViolationDetail
from cpn_core.types.api import ApiEnum
from cpn_telegram_bot.config_reader import config

logger = getLogger(__name__)


class GetData:
    @staticmethod
    async def get_data_single_plate(
        plate_info: PlateInfo,
    ) -> tuple[ViolationDetail, ...] | None:
        for api in config.APIS:
            engine: BaseGetDataEngine
            match api:
                case ApiEnum.checkphatnguoi_vn:
                    engine = CheckPhatNguoiEngine(timeout=config.REQUEST_TIMEOUT)
                case ApiEnum.csgt_vn:
                    engine = CsgtEngine(timeout=config.REQUEST_TIMEOUT)
                case ApiEnum.phatnguoi_vn:
                    engine = PhatNguoiEngine(timeout=config.REQUEST_TIMEOUT)
                case ApiEnum.zm_io_vn:
                    engine = ZmioEngine(timeout=config.REQUEST_TIMEOUT)
                case ApiEnum.etraffic_gtelict_vn:
                    if not config.ETRAFFIC_CITIZEN_ID or not config.ETRAFFIC_PASSWORD:
                        # FIXME: handle later
                        return None
                    engine = EtrafficEngine(
                        config.ETRAFFIC_CITIZEN_ID,
                        config.ETRAFFIC_PASSWORD,
                        timeout=config.REQUEST_TIMEOUT,
                    )
            async with engine:
                violation_details: (
                    tuple[ViolationDetail, ...] | None
                ) = await engine.get_data(plate_info)
                if violation_details is not None:
                    return violation_details

    def __init__(self, plate_infos: tuple[PlateInfo, ...]) -> None:
        self._checkphatnguoi_engine: CheckPhatNguoiEngine = CheckPhatNguoiEngine(
            timeout=config.REQUEST_TIMEOUT,
        )
        self._csgt_engine: CsgtEngine = CsgtEngine(
            timeout=config.REQUEST_TIMEOUT,
        )
        self._phatnguoi_engine: PhatNguoiEngine = PhatNguoiEngine(
            timeout=config.REQUEST_TIMEOUT,
        )
        self._zmio_engine: ZmioEngine = ZmioEngine(
            timeout=config.REQUEST_TIMEOUT,
        )
        self._etraffic_engine: EtrafficEngine | None = (
            EtrafficEngine(
                citizen_indentify=config.ETRAFFIC_CITIZEN_ID,
                password=config.ETRAFFIC_PASSWORD,
                timeout=config.REQUEST_TIMEOUT,
            )
            if config.ETRAFFIC_CITIZEN_ID is not None
            and config.ETRAFFIC_PASSWORD is not None
            else None
        )
        self._plate_infos: tuple[PlateInfo, ...] = plate_infos

    async def _get_data_for_plate(
        self,
        plate_info: PlateInfo,
    ) -> tuple[ViolationDetail, ...] | None:
        for api in config.APIS:
            engine: BaseGetDataEngine
            match api:
                case ApiEnum.checkphatnguoi_vn:
                    engine = self._checkphatnguoi_engine
                case ApiEnum.csgt_vn:
                    engine = self._csgt_engine
                case ApiEnum.phatnguoi_vn:
                    engine = self._phatnguoi_engine
                case ApiEnum.zm_io_vn:
                    engine = self._zmio_engine
                case ApiEnum.etraffic_gtelict_vn:
                    if not self._etraffic_engine:
                        logger.error(
                            "Plate %s - %s: You haven't given citizen ID and password!",
                            plate_info.plate,
                            ApiEnum.etraffic_gtelict_vn,
                        )
                        return
                    engine = self._etraffic_engine
            async with engine:
                violation_details: (
                    tuple[ViolationDetail, ...] | None
                ) = await engine.get_data(plate_info)
                if violation_details is not None:
                    return violation_details

    async def get_datas(self) -> tuple[tuple[ViolationDetail, ...] | None, ...]:
        async with (
            CheckPhatNguoiEngine(
                timeout=config.REQUEST_TIMEOUT,
            ) as self._checkphatnguoi_engine,
            CsgtEngine(
                timeout=config.REQUEST_TIMEOUT,
            ) as self._csgt_engine,
            PhatNguoiEngine(
                timeout=config.REQUEST_TIMEOUT,
            ) as self._phatnguoi_engine,
            ZmioEngine(
                timeout=config.REQUEST_TIMEOUT,
            ) as self._zmio_engine,
            self._etraffic_engine
            if self._etraffic_engine is not None
            else nullcontext(),
        ):
            return tuple(
                [
                    await self._get_data_for_plate(plate_info)
                    for plate_info in self._plate_infos
                ]
            )
