from enum import IntEnum

class Rr1700Command(IntEnum):
    IdleCommand = 0,
    BlinkCommand = 1,
    VoltageCommand = 2,
    MppCommand = 3,
    ReadCommand = 4,
    CurveCommand = 5,
    TransferCurveCommand = 6,
    ExternalMppCommand = 7,
    TriggeredCurveCommand = 8,
    GetStatus = 13,
    WriteEepromCommand = 14,
    SetTriggerCommand = 15,
    ReadEepromCommand = 16,
    UpdateConfigCommand = 17,
    GetConfigCommand = 18,
    StartFirmwareUpdate = 19,
    EnableFastCommunications = 20,
    DisableBroadcast = 21,
    TriggeredReadCommand = 50,
    Alive = 100,
    ListModules = 101,
    OpenModule = 106,
    CloseModule = 107,
    ResetModule = 108,
    ResetController = 109,
    TriggerAll = 110,
    BroadcastThresholdExceeded = 111,
    CurveRunning = 250

class Rr1700Function(IntEnum):
    IvMppReadIVPoint = 20,
    IvMppApplyState = 21,
    PvIrrReadIrradiances = 30

class IvMppState(IntEnum):
    Voc = 0,
    Isc = 1,
    Mpp = 2,
    VoltageBias = 3
