from DataTable import Table, Row
from Manager import Manager
from Utility import get_filename
import hjson

class PlacementDataRow(Row):
    label_list = ['A', 'B', 'C', 'D', 'E']

    def __init__(self, *args):
        super().__init__(*args)

    # Not always useful (e.g. fill_events may need to preserve flags or eventlabels)
    def _next_free_event(self):
        for c in PlacementDataRow.label_list:
            if getattr(self, f'EventStartFlag_{c}') != 0: continue
            if getattr(self, f'EventEndFlag_{c}') != 0: continue
            if getattr(self, f'EventLabel_{c}') != 'None': continue
            empty_params = True
            for i in range(1, 11):
                empty_params &= getattr(self, f'EventParam_{c}_{i}') == 'None'
            if not empty_params: continue
            break
        else:
            sys.exit(f'No free Events found for {self.key}')

        return c

    def copy_event(self, source):
        dest = self._next_free_event()
        assert source != dest

        # Copy everything from the given source to the destination
        d = getattr(self, f'EventType_{source}')
        setattr(self, f'EventType_{dest}', d)
        d = getattr(self, f'EventStartFlag_{source}')
        setattr(self, f'EventStartFlag_{dest}', d)
        d = getattr(self, f'EventEndFlag_{source}')
        setattr(self, f'EventEndFlag_{dest}', d)
        d = getattr(self, f'TimeZoneTriggerType_{source}')
        setattr(self, f'TimeZoneTriggerType_{dest}', d)
        d = getattr(self, f'EventLabel_{source}')
        setattr(self, f'EventLabel_{dest}', d)
        for i in range(1, 11):
            d = getattr(self, f'EventParam_{source}_{i}')
            setattr(self, f'EventParam_{dest}_{i}', d)

        return dest


class PlacementDataTable(Table):
    def __init__(self, data, row_class):
        super().__init__(data, row_class)
