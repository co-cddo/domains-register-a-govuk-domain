from django.core.management.base import BaseCommand
from request_a_govuk_domain.request import models

REGISTRAR_NAMES = [
    "100 Percent IT Limited",
    "123 connect",
    "Alba Core Systems Ltd",
    "Al-Barq Macintosh Electronics Ltd",
    "Alchemy Systems (Western) Ltd",
    "Aubergine 262 Ltd",
    "BB Online UK Ltd",
    "Better Brand Agency Limited",
    "Blue Sky Hosting Ltd",
    "Bongo IT Ltd",
    "BWP Creative Limited",
    "Cloud Next Limited",
    "CompuWeb Communications Services Ltd",
    "Consider IT Limited",
    "CSD Network Services Ltd",
    "Cuttlefish Multimedia Ltd",
    "DDS Services Limited",
    "Doughty Software",
    "Drakonim Limited",
    "Easy Internet Solutions Ltd",
    "Elite Limited",
    "Elynx",
    "Enix Limited",
    "Force36 Limited",
    "Function 28 Limited",
    "Geoxphere Ltd",
    "HCI Data Ltd",
    "Hertscom IT Ltd",
    "Host4u Limited",
    "Internet for Business Ltd",
    "JustHostMe Limited",
    "Lancaster University Network Services Limited",
    "Mike Henson",
    "Mythic Beasts Ltd",
    "nameSpace",
    "NetHosted Ltd",
    "Netistrar Ltd",
    "Nexus Data Systems Ltd",
    "Northumberland County Council",
    "NYES Digital - North Yorkshire Council",
    "On Screen",
    "OWA Digital Ltd.",
    "Pulse8design Ltd",
    "PumpkinPip Ltd",
    "reCoded Solutions Ltd",
    "SCIS UK Limited",
    "See Green Media Ltd",
    "Somerset Web Services",
    "Springbok Computers Ltd",
    "Stablepoint Limited",
    "The Bunker Secure Hosting Ltd",
    "The Networking People (TNP) Limited",
    "The Stationery Office Ltd",
    "Together Technology Ltd",
    "Total Web Solutions",
    "TRS Design Agency Limited",
    "Vantech Media",
    "VPW Systems (UK) Ltd",
    "Web Function Limited",
    "WJP Software Limited",
]


class Command(BaseCommand):
    help = "Create a sample application for local testing"

    def handle(self, *args, **options):
        if not models.Registrar.objects.first():
            for name in REGISTRAR_NAMES:
                models.Registrar.objects.create(name=name)
        else:
            print("Not adding initial Registrars as the table is already populated")
