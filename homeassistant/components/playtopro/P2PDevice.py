"""P2P Connection Hub."""

from array import array
import socket

from homeassistant.exceptions import HomeAssistantError


class P2PZone:
    """Defines an irrigation zone."""

    index: int
    on: bool
    auto_mode: bool
    eco_mode: bool
    sleep_mode: bool
    manual_mode_active: bool
    eco_mode_active: bool

    def __init__(self, index) -> None:
        """Initialize the Zone ready for use."""
        self.index = index


class P2PRequest:
    """Defines a request packet."""

    serial_number: int
    header: int
    packet: int
    length: int
    packet_counter: int
    data: bytearray

    def __init__(
        self, serial_number: int, packet: int, length: int, data: bytearray
    ) -> None:
        """Initialize the Request for use."""
        self.header = ord("$")
        self.serial_number = serial_number
        self.packet = packet
        self.packet_counter = 0
        self.length = length
        self.data = bytearray(self.length)
        if self.length > 0:
            self.data = data[0 : self.length]
        else:
            self.data = bytearray()

    def toBytes(self) -> bytearray:
        """Converts a request to a byte array ready for sending."""
        output: bytearray = bytearray()
        output = output + self.header.to_bytes(1, "little")
        output = output + self.serial_number.to_bytes(4, "little")
        output = output + self.packet.to_bytes(1, "little")
        output = output + self.packet_counter.to_bytes(1, "little")
        output = output + self.length.to_bytes(1, "little")
        if self.length > 0:
            output = output + self.data[0 : self.length]
        return output + b"!"


class P2PZoneManualModeRequest(P2PRequest):
    """Defines a zone manual mode request."""

    def __init__(self, serial_number: int, zone: int, state: bool) -> None:
        """Initialize the Request for use."""
        temp: bytearray = bytearray()
        temp = temp + state.to_bytes(1, "little")
        temp = temp + zone.to_bytes(1, "little")
        super().__init__(serial_number, 7, 2, temp)


class P2PAutoModeRequest(P2PRequest):
    """Defines a device auto mode request."""

    def __init__(self, serial_number: int, state: bool) -> None:
        """Initialize the Request for use."""
        temp: bytearray = bytearray()
        temp = temp + state.to_bytes(1, "little")
        super().__init__(serial_number, 5, 1, temp)


class P2PZoneAutoModeRequest(P2PRequest):
    """Defines a zone auto mode request."""

    def __init__(self, serial_number: int, zone: int, state: bool) -> None:
        """Initialize the Request for use."""
        temp: bytearray = bytearray()
        temp = temp + zone.to_bytes(1, "little")
        temp = temp + state.to_bytes(1, "little")
        super().__init__(serial_number, 6, 2, temp)


class P2PEcoModeRequest(P2PRequest):
    """Defines a device eco mode request."""

    def __init__(self, serial_number: int, state: bool) -> None:
        """Initialize the Request for use."""
        temp: bytearray = bytearray()
        temp = temp + state.to_bytes(1, "little")
        super().__init__(serial_number, 8, 1, temp)


class P2PZoneEcoModeRequest(P2PRequest):
    """Defines a zone eco mode request."""

    def __init__(self, serial_number: int, zone: int, state: bool) -> None:
        """Initialize the Request for use."""
        temp: bytearray = bytearray()
        temp = temp + zone.to_bytes(1, "little")
        temp = temp + state.to_bytes(1, "little")
        super().__init__(serial_number, 9, 2, temp)


class P2PZoneSleepModeRequest(P2PRequest):
    """Defines a zone sleep mode request."""

    def __init__(self, serial_number: int, zone: int, state: bool) -> None:
        """Initialize the Request for use."""
        temp: bytearray = bytearray()
        temp = temp + zone.to_bytes(1, "little")
        temp = temp + state.to_bytes(1, "little")
        super().__init__(serial_number, 14, 2, temp)


class P2PResponse:
    """Defines a response packet."""

    data: bytearray
    header: int
    serial_number: int
    packet: int
    packet_counter: int
    length: int

    def __init__(self, input: bytearray) -> None:
        """Initialize the Response for use."""
        self.data = input
        self.header = self.data[0]
        self.serial_number = int.from_bytes(self.data[1:4], "little")
        self.packet = int.from_bytes([self.data[5]], "little")
        self.packet_counter = int.from_bytes([self.data[6]], "little")
        self.length = int.from_bytes([self.data[7]], "little")


class P2PFirmwareResponse(P2PResponse):
    """Firmware response packet."""

    firmware: int

    def __init__(self, response: P2PResponse) -> None:
        """Takes a Response and parses out the current firmware."""

        super().__init__(response.data)
        if self.packet == 0:
            if self.length == 2:
                self.firmware = int.from_bytes(self.data[8:9], "little")
            else:
                raise P2PError(
                    "Unable to get firmware response, unexpected response size"
                )

        else:
            raise P2PError(
                "Unable to get firmware response, unexpected response packet"
            )


class P2PConfirmationResponse(P2PResponse):
    """Confirmation response packet."""

    result: bool

    def __init__(self, response: P2PResponse, packet: int) -> None:
        """Takes a Response and parses out the confirmation."""

        super().__init__(response.data)
        if self.packet == packet:
            if self.length == 1:
                self.result = int.from_bytes([self.data[8]], "little") > 0
            else:
                raise P2PError(
                    "Unable to get confirmation response, unexpected response size"
                )

        else:
            raise P2PError(
                "Unable to get confirmation response, unexpected response packet"
            )


class P2PStatusResponse(P2PResponse):
    """Status response packet."""

    zones: list[P2PZone]
    system_run: bool
    system_auto: bool
    eco_mode: bool
    eco_mode_zones: int
    eco_mode_factor: int

    def __init__(self, response: P2PResponse) -> None:
        """Takes a Response and parses out the current status."""

        super().__init__(response.data)

        if self.packet == 1:
            self.system_run = bool.from_bytes([self.data[8]], "little")
            self.system_auto = bool.from_bytes([self.data[9]], "little")
            self.actual_output = int.from_bytes([self.data[10]], "little")
            self.manual_mode_zones_active = int.from_bytes([self.data[11]], "little")
            self.auto_mode_zones = int.from_bytes([self.data[12]], "little")
            self.eco_mode = bool.from_bytes([self.data[13]], "little")
            self.eco_mode_zones = int.from_bytes([self.data[14]], "little")
            self.eco_mode_factor = int.from_bytes([self.data[15]], "little")
            self.eco_mode_zones_active = int.from_bytes([self.data[16]], "little")
            self.year = int.from_bytes(self.data[17:18], "little")
            self.month = int.from_bytes([self.data[19]], "little")
            self.day = int.from_bytes([self.data[20]], "little")
            self.day = int.from_bytes([self.data[21]], "little")
            self.hour = int.from_bytes([self.data[22]], "little")
            self.minute = int.from_bytes([self.data[23]], "little")
            self.second = int.from_bytes([self.data[24]], "little")
            self.sleep_mode = int.from_bytes([self.data[25]], "little")
            self.sleep_until_year = int.from_bytes(self.data[26:27], "little")
            self.sleep_until_month = int.from_bytes([self.data[28]], "little")
            self.sleep_until_day = int.from_bytes([self.data[29]], "little")
            self.sleep_until_day = int.from_bytes([self.data[30]], "little")
            self.sleep_until_hour = int.from_bytes([self.data[31]], "little")
            self.sleep_until_minute = int.from_bytes([self.data[32]], "little")
            self.sleep_until_second = int.from_bytes([self.data[33]], "little")
            self.sleep_mode_zones = int.from_bytes([self.data[34]], "little")
            self.zones: array = []

            for x in range(8):
                zone = P2PZone(x)
                zone.on = ((self.actual_output >> x) & 0x01) > 0
                zone.manual_mode_active = (
                    (self.manual_mode_zones_active >> x) & 0x01
                ) > 0
                zone.auto_mode = ((self.auto_mode_zones >> x) & 0x01) > 0
                zone.eco_mode = ((self.eco_mode_zones >> x) & 0x01) > 0
                zone.eco_mode_active = ((self.eco_mode_zones_active >> x) & 0x01) > 0
                zone.sleep_mode = ((self.sleep_mode_zones >> x) & 0x01) > 0
                self.zones.append(zone)

        else:
            raise P2PError("Unable to get status, unexpected response")


class P2PDevice:
    """Class to communicate with the LichenHub API."""

    ipv4: str
    serial_number: int

    def __init__(
        self,
        ipv4: str,
        serial_number: int,
    ) -> None:
        """Initialize the API and store the auth so we can make requests."""
        self.ipv4 = ipv4
        self.serial_number = serial_number

    async def async_get_firmware(self) -> P2PFirmwareResponse:
        """Get the current status of the lichen play."""
        request: P2PRequest = P2PRequest(self.serial_number, 0, 0, bytearray())

        response: P2PResponse = await self.async_get_response(request)

        return P2PFirmwareResponse(response)

    async def async_get_status(self) -> P2PStatusResponse:
        """Get the current status of the lichen play."""

        request: P2PRequest = P2PRequest(self.serial_number, 1, 0, bytearray())
        try:
            response: P2PResponse = await self.async_get_response(request)
        except P2PRequestError as e:
            raise P2PError(f"Unable to get status, {e.error}") from e
        return P2PStatusResponse(response)

    async def async_set_zone_manual_mode(
        self, zone: int, state: bool
    ) -> P2PConfirmationResponse:
        """Set manual mode for the given zone."""
        request: P2PZoneManualModeRequest = P2PZoneManualModeRequest(
            self.serial_number, zone, state
        )

        response: P2PResponse = await self.async_get_response(request)

        return P2PConfirmationResponse(response, request.packet)

    async def async_set_auto_mode(self, state: bool) -> P2PConfirmationResponse:
        """Set device auto mode for the given."""
        request: P2PAutoModeRequest = P2PAutoModeRequest(self.serial_number, state)

        response: P2PResponse = await self.async_get_response(request)

        return P2PConfirmationResponse(response, request.packet)

    async def async_set_zone_auto_mode(
        self, zone: int, state: bool
    ) -> P2PConfirmationResponse:
        """Set auto mode for the given zone."""
        request: P2PZoneAutoModeRequest = P2PZoneAutoModeRequest(
            self.serial_number, zone, state
        )

        response: P2PResponse = await self.async_get_response(request)

        return P2PConfirmationResponse(response, request.packet)

    async def async_set_eco_mode(self, state: bool) -> P2PConfirmationResponse:
        """Set device eco mode for the given."""
        request: P2PEcoModeRequest = P2PEcoModeRequest(self.serial_number, state)

        response: P2PResponse = await self.async_get_response(request)

        return P2PConfirmationResponse(response, request.packet)

    async def async_set_zone_eco_mode(
        self, zone: int, state: bool
    ) -> P2PConfirmationResponse:
        """Set eco mode for the given zone."""
        request: P2PZoneEcoModeRequest = P2PZoneEcoModeRequest(
            self.serial_number, zone, state
        )

        response: P2PResponse = await self.async_get_response(request)

        return P2PConfirmationResponse(response, request.packet)

    async def async_set_zone_sleep_mode(
        self, zone: int, state: bool
    ) -> P2PConfirmationResponse:
        """Set sleep mode for the given zone."""
        request: P2PZoneSleepModeRequest = P2PZoneSleepModeRequest(
            self.serial_number, zone, state
        )

        response: P2PResponse = await self.async_get_response(request)

        return P2PConfirmationResponse(response, request.packet)

    async def async_get_response(self, request: P2PRequest) -> P2PResponse:
        """Send a request to the divce."""

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((self.ipv4, 1233))
        except Exception as err:
            raise P2PRequestError("Connection failed") from err

        # print(request.toBytes())

        output = request.toBytes()

        sent: int = s.send(output)

        if sent == len(output):
            buffer: bytearray = bytearray(100)

            result: int = s.recv_into(buffer)

            s.close()

            if result > 0:
                response = P2PResponse(buffer)
                if response.header == ord("$"):
                    if response.packet == request.packet:
                        return response
                    raise P2PRequestError("Packet mismatch")
                raise P2PRequestError("Unexpected header")
            raise P2PRequestError("Check private key")
        raise P2PRequestError("Failed to send request")


class ConnectionFailed(HomeAssistantError):
    """Raised when an update has failed."""


class P2PError(HomeAssistantError):
    """Base class for P2P exceptions."""

    def __init__(self, error: str) -> None:
        """Initialize error."""
        super().__init__()
        self.error = error


class P2PRequestError(P2PError):
    """Error Requesting packet."""


class DeviceNotFoundError(P2PError):
    """No device found."""


class InvalidPrivateKeyError(P2PError):
    """Invalid private key."""
