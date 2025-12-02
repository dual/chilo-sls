from chilo_sls.base.event import BaseRecordsEvent
from chilo_sls.kinesis.record import Record


class Event(BaseRecordsEvent):

    def __init__(self, event, context=None, **kwargs):
        super().__init__(event, context, **kwargs)
        self._record_class = Record
