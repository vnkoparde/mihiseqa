from django.contrib import admin

# Register your models here.
#for x in ['Instruments', 'Operators', 'PrincipalInvestigators', 'Projects', 'Runs', 'SampleSheet', 'ReadStatsPerTile', 'PositionStatsPerTile']:
from .models import Instruments
admin.site.register(Instruments)

from .models import Operators
admin.site.register(Operators)

from .models import PrincipalInvestigators
admin.site.register(PrincipalInvestigators)

from .models import Projects
admin.site.register(Projects)

from .models import Runs
admin.site.register(Runs)

from .models import SampleSheet
admin.site.register(SampleSheet)

from .models import ReadStatsPerTile
admin.site.register(ReadStatsPerTile)

from .models import PositionStatsPerTile
admin.site.register(PositionStatsPerTile)
