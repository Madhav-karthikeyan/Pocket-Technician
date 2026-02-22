import streamlit as st
import json, os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Image as RLImage
import openpyxl
import requests
import pandas as pd
from datetime import datetime
from astral import moon
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
        Image, PageBreak
        )
import os



def get_moon_name(phase):
    if phase == 0:
        return "New Moon (Amavasya)"
    elif phase == 14:
        return "Full Moon (Pournami)"
    elif phase < 7:
        return "Waxing Crescent"
    elif phase < 14:
        return "Waxing Gibbous"
    elif phase < 21:
        return "Waning Gibbous"
    else:
        return "Waning Crescent"
# =====================================================
# CONFIG
# =====================================================
DATA_FILE = "farm_data.json"


# Reference chart: Count per kg → %Feed → Feed per 100k
REFERENCE_FEED_CHART = {
1000: {"feed_pct": 10.00, "feed_100k": 10.0},
999: {"feed_pct": 10.00, "feed_100k": 10.0},
998: {"feed_pct": 10.00, "feed_100k": 10.0},
997: {"feed_pct": 9.99, "feed_100k": 10.0},
996: {"feed_pct": 9.99, "feed_100k": 10.0},
995: {"feed_pct": 9.99, "feed_100k": 10.0},
994: {"feed_pct": 9.99, "feed_100k": 10.0},
993: {"feed_pct": 9.99, "feed_100k": 10.1},
992: {"feed_pct": 9.98, "feed_100k": 10.1},
991: {"feed_pct": 9.98, "feed_100k": 10.1},
990: {"feed_pct": 9.98, "feed_100k": 10.1},
989: {"feed_pct": 9.98, "feed_100k": 10.1},
988: {"feed_pct": 9.97, "feed_100k": 10.1},
987: {"feed_pct": 9.97, "feed_100k": 10.1},
986: {"feed_pct": 9.97, "feed_100k": 10.1},
985: {"feed_pct": 9.97, "feed_100k": 10.1},
984: {"feed_pct": 9.97, "feed_100k": 10.1},
983: {"feed_pct": 9.96, "feed_100k": 10.1},
982: {"feed_pct": 9.96, "feed_100k": 10.1},
981: {"feed_pct": 9.96, "feed_100k": 10.2},
980: {"feed_pct": 9.96, "feed_100k": 10.2},
979: {"feed_pct": 9.95, "feed_100k": 10.2},
978: {"feed_pct": 9.95, "feed_100k": 10.2},
977: {"feed_pct": 9.95, "feed_100k": 10.2},
976: {"feed_pct": 9.95, "feed_100k": 10.2},
975: {"feed_pct": 9.95, "feed_100k": 10.2},
974: {"feed_pct": 9.94, "feed_100k": 10.2},
973: {"feed_pct": 9.94, "feed_100k": 10.2},
972: {"feed_pct": 9.94, "feed_100k": 10.2},
971: {"feed_pct": 9.94, "feed_100k": 10.2},
970: {"feed_pct": 9.93, "feed_100k": 10.2},
969: {"feed_pct": 9.93, "feed_100k": 10.2},
968: {"feed_pct": 9.93, "feed_100k": 10.3},
967: {"feed_pct": 9.93, "feed_100k": 10.3},
966: {"feed_pct": 9.92, "feed_100k": 10.3},
965: {"feed_pct": 9.92, "feed_100k": 10.3},
964: {"feed_pct": 9.92, "feed_100k": 10.3},
963: {"feed_pct": 9.92, "feed_100k": 10.3},
962: {"feed_pct": 9.91, "feed_100k": 10.3},
961: {"feed_pct": 9.91, "feed_100k": 10.3},
960: {"feed_pct": 9.91, "feed_100k": 10.3},
959: {"feed_pct": 9.90, "feed_100k": 10.3},
958: {"feed_pct": 9.90, "feed_100k": 10.3},
957: {"feed_pct": 9.90, "feed_100k": 10.3},
956: {"feed_pct": 9.90, "feed_100k": 10.4},
955: {"feed_pct": 9.89, "feed_100k": 10.4},
954: {"feed_pct": 9.89, "feed_100k": 10.4},
953: {"feed_pct": 9.89, "feed_100k": 10.4},
952: {"feed_pct": 9.89, "feed_100k": 10.4},
951: {"feed_pct": 9.88, "feed_100k": 10.4},
950: {"feed_pct": 9.88, "feed_100k": 10.4},
949: {"feed_pct": 9.88, "feed_100k": 10.4},
948: {"feed_pct": 9.87, "feed_100k": 10.4},
947: {"feed_pct": 9.87, "feed_100k": 10.4},
946: {"feed_pct": 9.87, "feed_100k": 10.4},
945: {"feed_pct": 9.87, "feed_100k": 10.4},
944: {"feed_pct": 9.86, "feed_100k": 10.4},
943: {"feed_pct": 9.86, "feed_100k": 10.5},
942: {"feed_pct": 9.86, "feed_100k": 10.5},
941: {"feed_pct": 9.85, "feed_100k": 10.5},
940: {"feed_pct": 9.85, "feed_100k": 10.5},
939: {"feed_pct": 9.85, "feed_100k": 10.5},
938: {"feed_pct": 9.85, "feed_100k": 10.5},
937: {"feed_pct": 9.84, "feed_100k": 10.5},
936: {"feed_pct": 9.84, "feed_100k": 10.5},
935: {"feed_pct": 9.84, "feed_100k": 10.5},
934: {"feed_pct": 9.83, "feed_100k": 10.5},
933: {"feed_pct": 9.83, "feed_100k": 10.5},
932: {"feed_pct": 9.83, "feed_100k": 10.5},
931: {"feed_pct": 9.82, "feed_100k": 10.6},
930: {"feed_pct": 9.82, "feed_100k": 10.6},
929: {"feed_pct": 9.82, "feed_100k": 10.6},
928: {"feed_pct": 9.81, "feed_100k": 10.6},
927: {"feed_pct": 9.81, "feed_100k": 10.6},
926: {"feed_pct": 9.81, "feed_100k": 10.6},
925: {"feed_pct": 9.81, "feed_100k": 10.6},
924: {"feed_pct": 9.80, "feed_100k": 10.6},
923: {"feed_pct": 9.80, "feed_100k": 10.6},
922: {"feed_pct": 9.80, "feed_100k": 10.6},
921: {"feed_pct": 9.79, "feed_100k": 10.6},
920: {"feed_pct": 9.79, "feed_100k": 10.6},
919: {"feed_pct": 9.79, "feed_100k": 10.6},
918: {"feed_pct": 9.78, "feed_100k": 10.7},
917: {"feed_pct": 9.78, "feed_100k": 10.7},
916: {"feed_pct": 9.78, "feed_100k": 10.7},
915: {"feed_pct": 9.77, "feed_100k": 10.7},
914: {"feed_pct": 9.77, "feed_100k": 10.7},
913: {"feed_pct": 9.77, "feed_100k": 10.7},
912: {"feed_pct": 9.76, "feed_100k": 10.7},
911: {"feed_pct": 9.76, "feed_100k": 10.7},
910: {"feed_pct": 9.76, "feed_100k": 10.7},
909: {"feed_pct": 9.75, "feed_100k": 10.7},
908: {"feed_pct": 9.75, "feed_100k": 10.7},
907: {"feed_pct": 9.74, "feed_100k": 10.7},
906: {"feed_pct": 9.74, "feed_100k": 10.8},
905: {"feed_pct": 9.74, "feed_100k": 10.8},
904: {"feed_pct": 9.73, "feed_100k": 10.8},
903: {"feed_pct": 9.73, "feed_100k": 10.8},
902: {"feed_pct": 9.73, "feed_100k": 10.8},
901: {"feed_pct": 9.72, "feed_100k": 10.8},
900: {"feed_pct": 9.72, "feed_100k": 10.8},
899: {"feed_pct": 9.72, "feed_100k": 10.8},
898: {"feed_pct": 9.71, "feed_100k": 10.8},
897: {"feed_pct": 9.71, "feed_100k": 10.8},
896: {"feed_pct": 9.71, "feed_100k": 10.8},
895: {"feed_pct": 9.70, "feed_100k": 10.8},
894: {"feed_pct": 9.70, "feed_100k": 10.8},
893: {"feed_pct": 9.69, "feed_100k": 10.9},
892: {"feed_pct": 9.69, "feed_100k": 10.9},
891: {"feed_pct": 9.69, "feed_100k": 10.9},
890: {"feed_pct": 9.68, "feed_100k": 10.9},
889: {"feed_pct": 9.68, "feed_100k": 10.9},
888: {"feed_pct": 9.68, "feed_100k": 10.9},
887: {"feed_pct": 9.67, "feed_100k": 10.9},
886: {"feed_pct": 9.67, "feed_100k": 10.9},
885: {"feed_pct": 9.66, "feed_100k": 10.9},
884: {"feed_pct": 9.66, "feed_100k": 10.9},
883: {"feed_pct": 9.66, "feed_100k": 10.9},
882: {"feed_pct": 9.65, "feed_100k": 10.9},
881: {"feed_pct": 9.65, "feed_100k": 11.0},
880: {"feed_pct": 9.64, "feed_100k": 11.0},
879: {"feed_pct": 9.64, "feed_100k": 11.0},
878: {"feed_pct": 9.64, "feed_100k": 11.0},
877: {"feed_pct": 9.63, "feed_100k": 11.0},
876: {"feed_pct": 9.63, "feed_100k": 11.0},
875: {"feed_pct": 9.63, "feed_100k": 11.0},
874: {"feed_pct": 9.62, "feed_100k": 11.0},
873: {"feed_pct": 9.62, "feed_100k": 11.0},
872: {"feed_pct": 9.61, "feed_100k": 11.0},
871: {"feed_pct": 9.61, "feed_100k": 11.0},
870: {"feed_pct": 9.60, "feed_100k": 11.0},
869: {"feed_pct": 9.60, "feed_100k": 11.0},
868: {"feed_pct": 9.60, "feed_100k": 11.1},
867: {"feed_pct": 9.59, "feed_100k": 11.1},
866: {"feed_pct": 9.59, "feed_100k": 11.1},
865: {"feed_pct": 9.58, "feed_100k": 11.1},
864: {"feed_pct": 9.58, "feed_100k": 11.1},
863: {"feed_pct": 9.58, "feed_100k": 11.1},
862: {"feed_pct": 9.57, "feed_100k": 11.1},
861: {"feed_pct": 9.57, "feed_100k": 11.1},
860: {"feed_pct": 9.56, "feed_100k": 11.1},
859: {"feed_pct": 9.56, "feed_100k": 11.1},
858: {"feed_pct": 9.55, "feed_100k": 11.1},
857: {"feed_pct": 9.55, "feed_100k": 11.1},
856: {"feed_pct": 9.55, "feed_100k": 11.2},
855: {"feed_pct": 9.54, "feed_100k": 11.2},
854: {"feed_pct": 9.54, "feed_100k": 11.2},
853: {"feed_pct": 9.53, "feed_100k": 11.2},
852: {"feed_pct": 9.53, "feed_100k": 11.2},
851: {"feed_pct": 9.52, "feed_100k": 11.2},
850: {"feed_pct": 9.52, "feed_100k": 11.2},
849: {"feed_pct": 9.52, "feed_100k": 11.2},
848: {"feed_pct": 9.51, "feed_100k": 11.2},
847: {"feed_pct": 9.51, "feed_100k": 11.2},
846: {"feed_pct": 9.50, "feed_100k": 11.2},
845: {"feed_pct": 9.50, "feed_100k": 11.2},
844: {"feed_pct": 9.49, "feed_100k": 11.2},
843: {"feed_pct": 9.49, "feed_100k": 11.3},
842: {"feed_pct": 9.48, "feed_100k": 11.3},
841: {"feed_pct": 9.48, "feed_100k": 11.3},
840: {"feed_pct": 9.48, "feed_100k": 11.3},
839: {"feed_pct": 9.47, "feed_100k": 11.3},
838: {"feed_pct": 9.47, "feed_100k": 11.3},
837: {"feed_pct": 9.46, "feed_100k": 11.3},
836: {"feed_pct": 9.46, "feed_100k": 11.3},
835: {"feed_pct": 9.45, "feed_100k": 11.3},
834: {"feed_pct": 9.45, "feed_100k": 11.3},
833: {"feed_pct": 9.44, "feed_100k": 11.3},
832: {"feed_pct": 9.44, "feed_100k": 11.3},
831: {"feed_pct": 9.43, "feed_100k": 11.4},
830: {"feed_pct": 9.43, "feed_100k": 11.4},
829: {"feed_pct": 9.42, "feed_100k": 11.4},
828: {"feed_pct": 9.42, "feed_100k": 11.4},
827: {"feed_pct": 9.41, "feed_100k": 11.4},
826: {"feed_pct": 9.41, "feed_100k": 11.4},
825: {"feed_pct": 9.41, "feed_100k": 11.4},
824: {"feed_pct": 9.40, "feed_100k": 11.4},
823: {"feed_pct": 9.40, "feed_100k": 11.4},
822: {"feed_pct": 9.39, "feed_100k": 11.4},
821: {"feed_pct": 9.39, "feed_100k": 11.4},
820: {"feed_pct": 9.38, "feed_100k": 11.4},
819: {"feed_pct": 9.38, "feed_100k": 11.4},
818: {"feed_pct": 9.37, "feed_100k": 11.5},
817: {"feed_pct": 9.37, "feed_100k": 11.5},
816: {"feed_pct": 9.36, "feed_100k": 11.5},
815: {"feed_pct": 9.36, "feed_100k": 11.5},
814: {"feed_pct": 9.35, "feed_100k": 11.5},
813: {"feed_pct": 9.35, "feed_100k": 11.5},
812: {"feed_pct": 9.34, "feed_100k": 11.5},
811: {"feed_pct": 9.34, "feed_100k": 11.5},
810: {"feed_pct": 9.33, "feed_100k": 11.5},
809: {"feed_pct": 9.33, "feed_100k": 11.5},
808: {"feed_pct": 9.32, "feed_100k": 11.5},
807: {"feed_pct": 9.32, "feed_100k": 11.5},
806: {"feed_pct": 9.31, "feed_100k": 11.6},
805: {"feed_pct": 9.31, "feed_100k": 11.6},
804: {"feed_pct": 9.30, "feed_100k": 11.6},
803: {"feed_pct": 9.30, "feed_100k": 11.6},
802: {"feed_pct": 9.29, "feed_100k": 11.6},
801: {"feed_pct": 9.29, "feed_100k": 11.6},
800: {"feed_pct": 9.28, "feed_100k": 11.6},
799: {"feed_pct": 9.27, "feed_100k": 11.6},
798: {"feed_pct": 9.27, "feed_100k": 11.6},
797: {"feed_pct": 9.26, "feed_100k": 11.6},
796: {"feed_pct": 9.26, "feed_100k": 11.6},
795: {"feed_pct": 9.25, "feed_100k": 11.6},
794: {"feed_pct": 9.25, "feed_100k": 11.6},
793: {"feed_pct": 9.24, "feed_100k": 11.7},
792: {"feed_pct": 9.24, "feed_100k": 11.7},
791: {"feed_pct": 9.23, "feed_100k": 11.7},
790: {"feed_pct": 9.23, "feed_100k": 11.7},
789: {"feed_pct": 9.22, "feed_100k": 11.7},
788: {"feed_pct": 9.22, "feed_100k": 11.7},
787: {"feed_pct": 9.21, "feed_100k": 11.7},
786: {"feed_pct": 9.21, "feed_100k": 11.7},
785: {"feed_pct": 9.20, "feed_100k": 11.7},
784: {"feed_pct": 9.19, "feed_100k": 11.7},
783: {"feed_pct": 9.19, "feed_100k": 11.7},
782: {"feed_pct": 9.18, "feed_100k": 11.7},
781: {"feed_pct": 9.18, "feed_100k": 11.8},
780: {"feed_pct": 9.17, "feed_100k": 11.8},
779: {"feed_pct": 9.17, "feed_100k": 11.8},
778: {"feed_pct": 9.16, "feed_100k": 11.8},
777: {"feed_pct": 9.16, "feed_100k": 11.8},
776: {"feed_pct": 9.15, "feed_100k": 11.8},
775: {"feed_pct": 9.15, "feed_100k": 11.8},
774: {"feed_pct": 9.14, "feed_100k": 11.8},
773: {"feed_pct": 9.13, "feed_100k": 11.8},
772: {"feed_pct": 9.13, "feed_100k": 11.8},
771: {"feed_pct": 9.12, "feed_100k": 11.8},
770: {"feed_pct": 9.12, "feed_100k": 11.8},
769: {"feed_pct": 9.11, "feed_100k": 11.8},
768: {"feed_pct": 9.11, "feed_100k": 11.9},
767: {"feed_pct": 9.10, "feed_100k": 11.9},
766: {"feed_pct": 9.09, "feed_100k": 11.9},
765: {"feed_pct": 9.09, "feed_100k": 11.9},
764: {"feed_pct": 9.08, "feed_100k": 11.9},
763: {"feed_pct": 9.08, "feed_100k": 11.9},
762: {"feed_pct": 9.07, "feed_100k": 11.9},
761: {"feed_pct": 9.07, "feed_100k": 11.9},
760: {"feed_pct": 9.06, "feed_100k": 11.9},
759: {"feed_pct": 9.05, "feed_100k": 11.9},
758: {"feed_pct": 9.05, "feed_100k": 11.9},
757: {"feed_pct": 9.04, "feed_100k": 11.9},
756: {"feed_pct": 9.04, "feed_100k": 12.0},
755: {"feed_pct": 9.03, "feed_100k": 12.0},
754: {"feed_pct": 9.02, "feed_100k": 12.0},
753: {"feed_pct": 9.02, "feed_100k": 12.0},
752: {"feed_pct": 9.01, "feed_100k": 12.0},
751: {"feed_pct": 9.01, "feed_100k": 12.0},
750: {"feed_pct": 9.00, "feed_100k": 12.0},
749: {"feed_pct": 8.99, "feed_100k": 12.0},
748: {"feed_pct": 8.99, "feed_100k": 12.0},
747: {"feed_pct": 8.98, "feed_100k": 12.0},
746: {"feed_pct": 8.98, "feed_100k": 12.0},
745: {"feed_pct": 8.97, "feed_100k": 12.0},
744: {"feed_pct": 8.96, "feed_100k": 12.0},
743: {"feed_pct": 8.96, "feed_100k": 12.1},
742: {"feed_pct": 8.95, "feed_100k": 12.1},
741: {"feed_pct": 8.95, "feed_100k": 12.1},
740: {"feed_pct": 8.94, "feed_100k": 12.1},
739: {"feed_pct": 8.93, "feed_100k": 12.1},
738: {"feed_pct": 8.93, "feed_100k": 12.1},
737: {"feed_pct": 8.92, "feed_100k": 12.1},
736: {"feed_pct": 8.91, "feed_100k": 12.1},
735: {"feed_pct": 8.91, "feed_100k": 12.1},
734: {"feed_pct": 8.90, "feed_100k": 12.1},
733: {"feed_pct": 8.90, "feed_100k": 12.1},
732: {"feed_pct": 8.89, "feed_100k": 12.1},
731: {"feed_pct": 8.88, "feed_100k": 12.2},
730: {"feed_pct": 8.88, "feed_100k": 12.2},
729: {"feed_pct": 8.87, "feed_100k": 12.2},
728: {"feed_pct": 8.86, "feed_100k": 12.2},
727: {"feed_pct": 8.86, "feed_100k": 12.2},
726: {"feed_pct": 8.85, "feed_100k": 12.2},
725: {"feed_pct": 8.85, "feed_100k": 12.2},
724: {"feed_pct": 8.84, "feed_100k": 12.2},
723: {"feed_pct": 8.83, "feed_100k": 12.2},
722: {"feed_pct": 8.83, "feed_100k": 12.2},
721: {"feed_pct": 8.82, "feed_100k": 12.2},
720: {"feed_pct": 8.81, "feed_100k": 12.2},
719: {"feed_pct": 8.81, "feed_100k": 12.2},
718: {"feed_pct": 8.80, "feed_100k": 12.3},
717: {"feed_pct": 8.79, "feed_100k": 12.3},
716: {"feed_pct": 8.79, "feed_100k": 12.3},
715: {"feed_pct": 8.78, "feed_100k": 12.3},
714: {"feed_pct": 8.77, "feed_100k": 12.3},
713: {"feed_pct": 8.77, "feed_100k": 12.3},
712: {"feed_pct": 8.76, "feed_100k": 12.3},
711: {"feed_pct": 8.75, "feed_100k": 12.3},
710: {"feed_pct": 8.75, "feed_100k": 12.3},
709: {"feed_pct": 8.74, "feed_100k": 12.3},
708: {"feed_pct": 8.73, "feed_100k": 12.3},
707: {"feed_pct": 8.73, "feed_100k": 12.3},
706: {"feed_pct": 8.72, "feed_100k": 12.4},
705: {"feed_pct": 8.71, "feed_100k": 12.4},
704: {"feed_pct": 8.71, "feed_100k": 12.4},
703: {"feed_pct": 8.70, "feed_100k": 12.4},
702: {"feed_pct": 8.69, "feed_100k": 12.4},
701: {"feed_pct": 8.69, "feed_100k": 12.4},
700: {"feed_pct": 8.68, "feed_100k": 12.4},
699: {"feed_pct": 8.67, "feed_100k": 12.4},
698: {"feed_pct": 8.67, "feed_100k": 12.4},
697: {"feed_pct": 8.66, "feed_100k": 12.4},
696: {"feed_pct": 8.65, "feed_100k": 12.4},
695: {"feed_pct": 8.65, "feed_100k": 12.4},
694: {"feed_pct": 8.64, "feed_100k": 12.4},
693: {"feed_pct": 8.63, "feed_100k": 12.5},
692: {"feed_pct": 8.63, "feed_100k": 12.5},
691: {"feed_pct": 8.62, "feed_100k": 12.5},
690: {"feed_pct": 8.61, "feed_100k": 12.5},
689: {"feed_pct": 8.60, "feed_100k": 12.5},
688: {"feed_pct": 8.60, "feed_100k": 12.5},
687: {"feed_pct": 8.59, "feed_100k": 12.5},
686: {"feed_pct": 8.58, "feed_100k": 12.5},
685: {"feed_pct": 8.58, "feed_100k": 12.5},
684: {"feed_pct": 8.57, "feed_100k": 12.5},
683: {"feed_pct": 8.56, "feed_100k": 12.5},
682: {"feed_pct": 8.56, "feed_100k": 12.5},
681: {"feed_pct": 8.55, "feed_100k": 12.6},
680: {"feed_pct": 8.54, "feed_100k": 12.6},
679: {"feed_pct": 8.53, "feed_100k": 12.6},
678: {"feed_pct": 8.53, "feed_100k": 12.6},
677: {"feed_pct": 8.52, "feed_100k": 12.6},
676: {"feed_pct": 8.51, "feed_100k": 12.6},
675: {"feed_pct": 8.51, "feed_100k": 12.6},
674: {"feed_pct": 8.50, "feed_100k": 12.6},
673: {"feed_pct": 8.49, "feed_100k": 12.6},
672: {"feed_pct": 8.48, "feed_100k": 12.6},
671: {"feed_pct": 8.48, "feed_100k": 12.6},
670: {"feed_pct": 8.47, "feed_100k": 12.6},
669: {"feed_pct": 8.46, "feed_100k": 12.6},
668: {"feed_pct": 8.45, "feed_100k": 12.7},
667: {"feed_pct": 8.45, "feed_100k": 12.7},
666: {"feed_pct": 8.44, "feed_100k": 12.7},
665: {"feed_pct": 8.43, "feed_100k": 12.7},
664: {"feed_pct": 8.42, "feed_100k": 12.7},
663: {"feed_pct": 8.42, "feed_100k": 12.7},
662: {"feed_pct": 8.41, "feed_100k": 12.7},
661: {"feed_pct": 8.40, "feed_100k": 12.7},
660: {"feed_pct": 8.40, "feed_100k": 12.7},
659: {"feed_pct": 8.39, "feed_100k": 12.7},
658: {"feed_pct": 8.38, "feed_100k": 12.7},
657: {"feed_pct": 8.37, "feed_100k": 12.7},
656: {"feed_pct": 8.37, "feed_100k": 12.8},
655: {"feed_pct": 8.36, "feed_100k": 12.8},
654: {"feed_pct": 8.35, "feed_100k": 12.8},
653: {"feed_pct": 8.34, "feed_100k": 12.8},
652: {"feed_pct": 8.34, "feed_100k": 12.8},
651: {"feed_pct": 8.33, "feed_100k": 12.8},
650: {"feed_pct": 8.32, "feed_100k": 12.8},
649: {"feed_pct": 8.31, "feed_100k": 12.8},
648: {"feed_pct": 8.30, "feed_100k": 12.8},
647: {"feed_pct": 8.30, "feed_100k": 12.8},
646: {"feed_pct": 8.29, "feed_100k": 12.8},
645: {"feed_pct": 8.28, "feed_100k": 12.8},
644: {"feed_pct": 8.27, "feed_100k": 12.8},
643: {"feed_pct": 8.27, "feed_100k": 12.9},
642: {"feed_pct": 8.26, "feed_100k": 12.9},
641: {"feed_pct": 8.25, "feed_100k": 12.9},
640: {"feed_pct": 8.24, "feed_100k": 12.9},
639: {"feed_pct": 8.24, "feed_100k": 12.9},
638: {"feed_pct": 8.23, "feed_100k": 12.9},
637: {"feed_pct": 8.22, "feed_100k": 12.9},
636: {"feed_pct": 8.21, "feed_100k": 12.9},
635: {"feed_pct": 8.20, "feed_100k": 12.9},
634: {"feed_pct": 8.20, "feed_100k": 12.9},
633: {"feed_pct": 8.19, "feed_100k": 12.9},
632: {"feed_pct": 8.18, "feed_100k": 12.9},
631: {"feed_pct": 8.17, "feed_100k": 13.0},
630: {"feed_pct": 8.16, "feed_100k": 13.0},
629: {"feed_pct": 8.16, "feed_100k": 13.0},
628: {"feed_pct": 8.15, "feed_100k": 13.0},
627: {"feed_pct": 8.14, "feed_100k": 13.0},
626: {"feed_pct": 8.13, "feed_100k": 13.0},
625: {"feed_pct": 8.13, "feed_100k": 13.0},
624: {"feed_pct": 8.12, "feed_100k": 13.0},
623: {"feed_pct": 8.11, "feed_100k": 13.0},
622: {"feed_pct": 8.10, "feed_100k": 13.0},
621: {"feed_pct": 8.09, "feed_100k": 13.0},
620: {"feed_pct": 8.08, "feed_100k": 13.0},
619: {"feed_pct": 8.08, "feed_100k": 13.0},
618: {"feed_pct": 8.07, "feed_100k": 13.1},
617: {"feed_pct": 8.06, "feed_100k": 13.1},
616: {"feed_pct": 8.05, "feed_100k": 13.1},
615: {"feed_pct": 8.04, "feed_100k": 13.1},
614: {"feed_pct": 8.04, "feed_100k": 13.1},
613: {"feed_pct": 8.03, "feed_100k": 13.1},
612: {"feed_pct": 8.02, "feed_100k": 13.1},
611: {"feed_pct": 8.01, "feed_100k": 13.1},
610: {"feed_pct": 8.00, "feed_100k": 13.1},
609: {"feed_pct": 7.99, "feed_100k": 13.1},
608: {"feed_pct": 7.99, "feed_100k": 13.1},
607: {"feed_pct": 7.98, "feed_100k": 13.1},
606: {"feed_pct": 7.97, "feed_100k": 13.2},
605: {"feed_pct": 7.96, "feed_100k": 13.2},
604: {"feed_pct": 7.95, "feed_100k": 13.2},
603: {"feed_pct": 7.95, "feed_100k": 13.2},
602: {"feed_pct": 7.94, "feed_100k": 13.2},
601: {"feed_pct": 7.93, "feed_100k": 13.2},
600: {"feed_pct": 7.92, "feed_100k": 13.2},
599: {"feed_pct": 7.91, "feed_100k": 13.2},
598: {"feed_pct": 7.90, "feed_100k": 13.2},
597: {"feed_pct": 7.89, "feed_100k": 13.2},
596: {"feed_pct": 7.89, "feed_100k": 13.2},
595: {"feed_pct": 7.88, "feed_100k": 13.2},
594: {"feed_pct": 7.87, "feed_100k": 13.2},
593: {"feed_pct": 7.86, "feed_100k": 13.3},
592: {"feed_pct": 7.85, "feed_100k": 13.3},
591: {"feed_pct": 7.84, "feed_100k": 13.3},
590: {"feed_pct": 7.84, "feed_100k": 13.3},
589: {"feed_pct": 7.83, "feed_100k": 13.3},
588: {"feed_pct": 7.82, "feed_100k": 13.3},
587: {"feed_pct": 7.81, "feed_100k": 13.3},
586: {"feed_pct": 7.80, "feed_100k": 13.3},
585: {"feed_pct": 7.79, "feed_100k": 13.3},
584: {"feed_pct": 7.78, "feed_100k": 13.3},
583: {"feed_pct": 7.77, "feed_100k": 13.3},
582: {"feed_pct": 7.77, "feed_100k": 13.3},
581: {"feed_pct": 7.76, "feed_100k": 13.4},
580: {"feed_pct": 7.75, "feed_100k": 13.4},
579: {"feed_pct": 7.74, "feed_100k": 13.4},
578: {"feed_pct": 7.73, "feed_100k": 13.4},
577: {"feed_pct": 7.72, "feed_100k": 13.4},
576: {"feed_pct": 7.71, "feed_100k": 13.4},
575: {"feed_pct": 7.71, "feed_100k": 13.4},
574: {"feed_pct": 7.70, "feed_100k": 13.4},
573: {"feed_pct": 7.69, "feed_100k": 13.4},
572: {"feed_pct": 7.68, "feed_100k": 13.4},
571: {"feed_pct": 7.67, "feed_100k": 13.4},
570: {"feed_pct": 7.66, "feed_100k": 13.4},
569: {"feed_pct": 7.65, "feed_100k": 13.4},
568: {"feed_pct": 7.64, "feed_100k": 13.5},
567: {"feed_pct": 7.63, "feed_100k": 13.5},
566: {"feed_pct": 7.63, "feed_100k": 13.5},
565: {"feed_pct": 7.62, "feed_100k": 13.5},
564: {"feed_pct": 7.61, "feed_100k": 13.5},
563: {"feed_pct": 7.60, "feed_100k": 13.5},
562: {"feed_pct": 7.59, "feed_100k": 13.5},
561: {"feed_pct": 7.58, "feed_100k": 13.5},
560: {"feed_pct": 7.57, "feed_100k": 13.5},
559: {"feed_pct": 7.56, "feed_100k": 13.5},
558: {"feed_pct": 7.55, "feed_100k": 13.5},
557: {"feed_pct": 7.54, "feed_100k": 13.5},
556: {"feed_pct": 7.53, "feed_100k": 13.6},
555: {"feed_pct": 7.53, "feed_100k": 13.6},
554: {"feed_pct": 7.52, "feed_100k": 13.6},
553: {"feed_pct": 7.51, "feed_100k": 13.6},
552: {"feed_pct": 7.50, "feed_100k": 13.6},
551: {"feed_pct": 7.49, "feed_100k": 13.6},
550: {"feed_pct": 7.48, "feed_100k": 13.6},
549: {"feed_pct": 7.47, "feed_100k": 13.6},
548: {"feed_pct": 7.46, "feed_100k": 13.6},
547: {"feed_pct": 7.45, "feed_100k": 13.6},
546: {"feed_pct": 7.44, "feed_100k": 13.6},
545: {"feed_pct": 7.43, "feed_100k": 13.6},
544: {"feed_pct": 7.42, "feed_100k": 13.6},
543: {"feed_pct": 7.42, "feed_100k": 13.7},
542: {"feed_pct": 7.41, "feed_100k": 13.7},
541: {"feed_pct": 7.40, "feed_100k": 13.7},
540: {"feed_pct": 7.39, "feed_100k": 13.7},
539: {"feed_pct": 7.38, "feed_100k": 13.7},
538: {"feed_pct": 7.37, "feed_100k": 13.7},
537: {"feed_pct": 7.36, "feed_100k": 13.7},
536: {"feed_pct": 7.35, "feed_100k": 13.7},
535: {"feed_pct": 7.34, "feed_100k": 13.7},
534: {"feed_pct": 7.33, "feed_100k": 13.7},
533: {"feed_pct": 7.32, "feed_100k": 13.7},
532: {"feed_pct": 7.31, "feed_100k": 13.7},
531: {"feed_pct": 7.30, "feed_100k": 13.8},
530: {"feed_pct": 7.29, "feed_100k": 13.8},
529: {"feed_pct": 7.28, "feed_100k": 13.8},
528: {"feed_pct": 7.27, "feed_100k": 13.8},
527: {"feed_pct": 7.26, "feed_100k": 13.8},
526: {"feed_pct": 7.25, "feed_100k": 13.8},
525: {"feed_pct": 7.25, "feed_100k": 13.8},
524: {"feed_pct": 7.24, "feed_100k": 13.8},
523: {"feed_pct": 7.23, "feed_100k": 13.8},
522: {"feed_pct": 7.22, "feed_100k": 13.8},
521: {"feed_pct": 7.21, "feed_100k": 13.8},
520: {"feed_pct": 7.20, "feed_100k": 13.8},
519: {"feed_pct": 7.19, "feed_100k": 13.8},
518: {"feed_pct": 7.18, "feed_100k": 13.9},
517: {"feed_pct": 7.17, "feed_100k": 13.9},
516: {"feed_pct": 7.16, "feed_100k": 13.9},
515: {"feed_pct": 7.15, "feed_100k": 13.9},
514: {"feed_pct": 7.14, "feed_100k": 13.9},
513: {"feed_pct": 7.13, "feed_100k": 13.9},
512: {"feed_pct": 7.12, "feed_100k": 13.9},
511: {"feed_pct": 7.11, "feed_100k": 13.9},
510: {"feed_pct": 7.10, "feed_100k": 13.9},
509: {"feed_pct": 7.09, "feed_100k": 13.9},
508: {"feed_pct": 7.08, "feed_100k": 13.9},
507: {"feed_pct": 7.07, "feed_100k": 13.9},
506: {"feed_pct": 7.06, "feed_100k": 14.0},
505: {"feed_pct": 7.05, "feed_100k": 14.0},
504: {"feed_pct": 7.04, "feed_100k": 14.0},
503: {"feed_pct": 7.03, "feed_100k": 14.0},
502: {"feed_pct": 7.02, "feed_100k": 14.0},
501: {"feed_pct": 7.01, "feed_100k": 14.0},
500: {"feed_pct": 7.00, "feed_100k": 14.0},
499: {"feed_pct": 6.99, "feed_100k": 14.0},
498: {"feed_pct": 6.98, "feed_100k": 14.0},
497: {"feed_pct": 6.97, "feed_100k": 14.0},
496: {"feed_pct": 6.96, "feed_100k": 14.0},
495: {"feed_pct": 6.95, "feed_100k": 14.0},
494: {"feed_pct": 6.94, "feed_100k": 14.0},
493: {"feed_pct": 6.93, "feed_100k": 14.1},
492: {"feed_pct": 6.92, "feed_100k": 14.1},
491: {"feed_pct": 6.91, "feed_100k": 14.1},
490: {"feed_pct": 6.90, "feed_100k": 14.1},
489: {"feed_pct": 6.89, "feed_100k": 14.1},
488: {"feed_pct": 6.88, "feed_100k": 14.1},
487: {"feed_pct": 6.87, "feed_100k": 14.1},
486: {"feed_pct": 6.86, "feed_100k": 14.1},
485: {"feed_pct": 6.85, "feed_100k": 14.1},
484: {"feed_pct": 6.84, "feed_100k": 14.1},
483: {"feed_pct": 6.83, "feed_100k": 14.2},
482: {"feed_pct": 6.82, "feed_100k": 14.2},
481: {"feed_pct": 6.81, "feed_100k": 14.2},
480: {"feed_pct": 6.80, "feed_100k": 14.2},
479: {"feed_pct": 6.79, "feed_100k": 14.2},
478: {"feed_pct": 6.78, "feed_100k": 14.2},
477: {"feed_pct": 6.77, "feed_100k": 14.2},
476: {"feed_pct": 6.76, "feed_100k": 14.2},
475: {"feed_pct": 6.75, "feed_100k": 14.2},
474: {"feed_pct": 6.74, "feed_100k": 14.3},
473: {"feed_pct": 6.73, "feed_100k": 14.3},
472: {"feed_pct": 6.72, "feed_100k": 14.3},
471: {"feed_pct": 6.71, "feed_100k": 14.3},
470: {"feed_pct": 6.70, "feed_100k": 14.3},
469: {"feed_pct": 6.69, "feed_100k": 14.3},
468: {"feed_pct": 6.68, "feed_100k": 14.3},
467: {"feed_pct": 6.67, "feed_100k": 14.3},
466: {"feed_pct": 6.66, "feed_100k": 14.3},
465: {"feed_pct": 6.65, "feed_100k": 14.4},
464: {"feed_pct": 6.64, "feed_100k": 14.4},
463: {"feed_pct": 6.63, "feed_100k": 14.4},
462: {"feed_pct": 6.62, "feed_100k": 14.4},
461: {"feed_pct": 6.61, "feed_100k": 14.4},
460: {"feed_pct": 6.60, "feed_100k": 14.4},
459: {"feed_pct": 6.59, "feed_100k": 14.4},
458: {"feed_pct": 6.58, "feed_100k": 14.4},
457: {"feed_pct": 6.57, "feed_100k": 14.4},
456: {"feed_pct": 6.56, "feed_100k": 14.5},
455: {"feed_pct": 6.55, "feed_100k": 14.5},
454: {"feed_pct": 6.54, "feed_100k": 14.5},
453: {"feed_pct": 6.53, "feed_100k": 14.5},
452: {"feed_pct": 6.52, "feed_100k": 14.5},
451: {"feed_pct": 6.51, "feed_100k": 14.5},
450: {"feed_pct": 6.50, "feed_100k": 14.5},
449: {"feed_pct": 6.86, "feed_100k": 15.3},
448: {"feed_pct": 6.85, "feed_100k": 15.3},
447: {"feed_pct": 6.85, "feed_100k": 15.3},
446: {"feed_pct": 6.85, "feed_100k": 15.4},
445: {"feed_pct": 6.84, "feed_100k": 15.4},
444: {"feed_pct": 6.84, "feed_100k": 15.4},
443: {"feed_pct": 6.83, "feed_100k": 15.4},
442: {"feed_pct": 6.83, "feed_100k": 15.5},
441: {"feed_pct": 6.82, "feed_100k": 15.5},
440: {"feed_pct": 6.82, "feed_100k": 15.5},
439: {"feed_pct": 6.82, "feed_100k": 15.5},
438: {"feed_pct": 6.81, "feed_100k": 15.6},
437: {"feed_pct": 6.81, "feed_100k": 15.6},
436: {"feed_pct": 6.80, "feed_100k": 15.6},
435: {"feed_pct": 6.80, "feed_100k": 15.6},
434: {"feed_pct": 6.79, "feed_100k": 15.7},
433: {"feed_pct": 6.79, "feed_100k": 15.7},
432: {"feed_pct": 6.78, "feed_100k": 15.7},
431: {"feed_pct": 6.78, "feed_100k": 15.7},
430: {"feed_pct": 6.77, "feed_100k": 15.8},
429: {"feed_pct": 6.77, "feed_100k": 15.8},
428: {"feed_pct": 6.76, "feed_100k": 15.8},
427: {"feed_pct": 6.76, "feed_100k": 15.8},
426: {"feed_pct": 6.75, "feed_100k": 15.9},
425: {"feed_pct": 6.75, "feed_100k": 15.9},
424: {"feed_pct": 6.74, "feed_100k": 15.9},
423: {"feed_pct": 6.74, "feed_100k": 15.9},
422: {"feed_pct": 6.73, "feed_100k": 16.0},
421: {"feed_pct": 6.73, "feed_100k": 16.0},
420: {"feed_pct": 6.72, "feed_100k": 16.0},
419: {"feed_pct": 6.71, "feed_100k": 16.0},
418: {"feed_pct": 6.71, "feed_100k": 16.1},
417: {"feed_pct": 6.70, "feed_100k": 16.1},
416: {"feed_pct": 6.70, "feed_100k": 16.1},
415: {"feed_pct": 6.69, "feed_100k": 16.1},
414: {"feed_pct": 6.69, "feed_100k": 16.2},
413: {"feed_pct": 6.68, "feed_100k": 16.2},
412: {"feed_pct": 6.67, "feed_100k": 16.2},
411: {"feed_pct": 6.67, "feed_100k": 16.2},
410: {"feed_pct": 6.66, "feed_100k": 16.3},
409: {"feed_pct": 6.66, "feed_100k": 16.3},
408: {"feed_pct": 6.65, "feed_100k": 16.3},
407: {"feed_pct": 6.64, "feed_100k": 16.3},
406: {"feed_pct": 6.64, "feed_100k": 16.4},
405: {"feed_pct": 6.63, "feed_100k": 16.4},
404: {"feed_pct": 6.63, "feed_100k": 16.4},
403: {"feed_pct": 6.62, "feed_100k": 16.4},
402: {"feed_pct": 6.61, "feed_100k": 16.5},
401: {"feed_pct": 6.61, "feed_100k": 16.5},
400: {"feed_pct": 6.60, "feed_100k": 16.5},
399: {"feed_pct": 6.59, "feed_100k": 16.5},
398: {"feed_pct": 6.58, "feed_100k": 16.5},
397: {"feed_pct": 6.57, "feed_100k": 16.6},
396: {"feed_pct": 6.57, "feed_100k": 16.6},
395: {"feed_pct": 6.56, "feed_100k": 16.6},
394: {"feed_pct": 6.55, "feed_100k": 16.6},
393: {"feed_pct": 6.54, "feed_100k": 16.6},
392: {"feed_pct": 6.53, "feed_100k": 16.7},
391: {"feed_pct": 6.52, "feed_100k": 16.7},
390: {"feed_pct": 6.51, "feed_100k": 16.7},
389: {"feed_pct": 6.50, "feed_100k": 16.7},
388: {"feed_pct": 6.50, "feed_100k": 16.7},
387: {"feed_pct": 6.49, "feed_100k": 16.8},
386: {"feed_pct": 6.48, "feed_100k": 16.8},
385: {"feed_pct": 6.47, "feed_100k": 16.8},
384: {"feed_pct": 6.46, "feed_100k": 16.8},
383: {"feed_pct": 6.45, "feed_100k": 16.8},
382: {"feed_pct": 6.44, "feed_100k": 16.9},
381: {"feed_pct": 6.43, "feed_100k": 16.9},
380: {"feed_pct": 6.42, "feed_100k": 16.9},
379: {"feed_pct": 6.41, "feed_100k": 16.9},
378: {"feed_pct": 6.40, "feed_100k": 16.9},
377: {"feed_pct": 6.39, "feed_100k": 17.0},
376: {"feed_pct": 6.38, "feed_100k": 17.0},
375: {"feed_pct": 6.38, "feed_100k": 17.0},
374: {"feed_pct": 6.37, "feed_100k": 17.0},
373: {"feed_pct": 6.36, "feed_100k": 17.0},
372: {"feed_pct": 6.35, "feed_100k": 17.1},
371: {"feed_pct": 6.34, "feed_100k": 17.1},
370: {"feed_pct": 6.33, "feed_100k": 17.1},
369: {"feed_pct": 6.32, "feed_100k": 17.1},
368: {"feed_pct": 6.31, "feed_100k": 17.1},
367: {"feed_pct": 6.30, "feed_100k": 17.2},
366: {"feed_pct": 6.29, "feed_100k": 17.2},
365: {"feed_pct": 6.28, "feed_100k": 17.2},
364: {"feed_pct": 6.27, "feed_100k": 17.2},
363: {"feed_pct": 6.26, "feed_100k": 17.2},
362: {"feed_pct": 6.25, "feed_100k": 17.3},
361: {"feed_pct": 6.24, "feed_100k": 17.3},
360: {"feed_pct": 6.23, "feed_100k": 17.3},
359: {"feed_pct": 6.22, "feed_100k": 17.3},
358: {"feed_pct": 6.21, "feed_100k": 17.3},
357: {"feed_pct": 6.20, "feed_100k": 17.4},
356: {"feed_pct": 6.19, "feed_100k": 17.4},
355: {"feed_pct": 6.18, "feed_100k": 17.4},
354: {"feed_pct": 6.17, "feed_100k": 17.4},
353: {"feed_pct": 6.16, "feed_100k": 17.4},
352: {"feed_pct": 6.15, "feed_100k": 17.5},
351: {"feed_pct": 6.14, "feed_100k": 17.5},
350: {"feed_pct": 6.13, "feed_100k": 17.5},
349: {"feed_pct": 6.11, "feed_100k": 17.5},
348: {"feed_pct": 6.10, "feed_100k": 17.5},
347: {"feed_pct": 6.09, "feed_100k": 17.6},
346: {"feed_pct": 6.08, "feed_100k": 17.6},
345: {"feed_pct": 6.07, "feed_100k": 17.6},
344: {"feed_pct": 6.06, "feed_100k": 17.6},
343: {"feed_pct": 6.05, "feed_100k": 17.6},
342: {"feed_pct": 6.04, "feed_100k": 17.7},
341: {"feed_pct": 6.03, "feed_100k": 17.7},
340: {"feed_pct": 6.02, "feed_100k": 17.7},
339: {"feed_pct": 6.01, "feed_100k": 17.7},
338: {"feed_pct": 6.00, "feed_100k": 17.7},
337: {"feed_pct": 5.99, "feed_100k": 17.8},
336: {"feed_pct": 5.97, "feed_100k": 17.8},
335: {"feed_pct": 5.96, "feed_100k": 17.8},
334: {"feed_pct": 5.95, "feed_100k": 17.8},
333: {"feed_pct": 5.99, "feed_100k": 18.0},
332: {"feed_pct": 5.98, "feed_100k": 18.0},
331: {"feed_pct": 5.97, "feed_100k": 18.0},
330: {"feed_pct": 5.96, "feed_100k": 18.1},
329: {"feed_pct": 5.95, "feed_100k": 18.1},
328: {"feed_pct": 5.94, "feed_100k": 18.1},
327: {"feed_pct": 5.93, "feed_100k": 18.1},
326: {"feed_pct": 5.92, "feed_100k": 18.2},
325: {"feed_pct": 5.91, "feed_100k": 18.2},
324: {"feed_pct": 5.90, "feed_100k": 18.2},
323: {"feed_pct": 5.89, "feed_100k": 18.2},
322: {"feed_pct": 5.88, "feed_100k": 18.3},
321: {"feed_pct": 5.87, "feed_100k": 18.3},
320: {"feed_pct": 5.86, "feed_100k": 18.3},
319: {"feed_pct": 5.85, "feed_100k": 18.3},
318: {"feed_pct": 5.84, "feed_100k": 18.4},
317: {"feed_pct": 5.83, "feed_100k": 18.4},
316: {"feed_pct": 5.82, "feed_100k": 18.4},
315: {"feed_pct": 5.81, "feed_100k": 18.4},
314: {"feed_pct": 5.80, "feed_100k": 18.5},
313: {"feed_pct": 5.78, "feed_100k": 18.5},
312: {"feed_pct": 5.77, "feed_100k": 18.5},
311: {"feed_pct": 5.76, "feed_100k": 18.5},
310: {"feed_pct": 5.75, "feed_100k": 18.6},
309: {"feed_pct": 5.74, "feed_100k": 18.6},
308: {"feed_pct": 5.73, "feed_100k": 18.6},
307: {"feed_pct": 5.72, "feed_100k": 18.6},
306: {"feed_pct": 5.71, "feed_100k": 18.6},
305: {"feed_pct": 5.69, "feed_100k": 18.7},
304: {"feed_pct": 5.68, "feed_100k": 18.7},
303: {"feed_pct": 5.67, "feed_100k": 18.7},
302: {"feed_pct": 5.66, "feed_100k": 18.7},
301: {"feed_pct": 5.65, "feed_100k": 18.8},
300: {"feed_pct": 5.64, "feed_100k": 18.8},
299: {"feed_pct": 5.63, "feed_100k": 18.8},
298: {"feed_pct": 5.61, "feed_100k": 18.8},
297: {"feed_pct": 5.60, "feed_100k": 18.9},
296: {"feed_pct": 5.59, "feed_100k": 18.9},
295: {"feed_pct": 5.58, "feed_100k": 18.9},
294: {"feed_pct": 5.57, "feed_100k": 18.9},
293: {"feed_pct": 5.56, "feed_100k": 19.0},
292: {"feed_pct": 5.54, "feed_100k": 19.0},
291: {"feed_pct": 5.53, "feed_100k": 19.0},
290: {"feed_pct": 5.52, "feed_100k": 19.0},
289: {"feed_pct": 5.51, "feed_100k": 19.1},
288: {"feed_pct": 5.50, "feed_100k": 19.1},
287: {"feed_pct": 5.48, "feed_100k": 19.1},
286: {"feed_pct": 5.47, "feed_100k": 19.1},
285: {"feed_pct": 5.46, "feed_100k": 19.2},
284: {"feed_pct": 5.45, "feed_100k": 19.2},
283: {"feed_pct": 5.43, "feed_100k": 19.2},
282: {"feed_pct": 5.42, "feed_100k": 19.2},
281: {"feed_pct": 5.41, "feed_100k": 19.2},
280: {"feed_pct": 5.40, "feed_100k": 19.3},
279: {"feed_pct": 5.38, "feed_100k": 19.3},
278: {"feed_pct": 5.37, "feed_100k": 19.3},
277: {"feed_pct": 5.36, "feed_100k": 19.3},
276: {"feed_pct": 5.35, "feed_100k": 19.4},
275: {"feed_pct": 5.33, "feed_100k": 19.4},
274: {"feed_pct": 5.32, "feed_100k": 19.4},
273: {"feed_pct": 5.31, "feed_100k": 19.4},
272: {"feed_pct": 5.29, "feed_100k": 19.5},
271: {"feed_pct": 5.28, "feed_100k": 19.5},
270: {"feed_pct": 5.27, "feed_100k": 19.5},
269: {"feed_pct": 5.26, "feed_100k": 19.5},
268: {"feed_pct": 5.24, "feed_100k": 19.6},
267: {"feed_pct": 5.23, "feed_100k": 19.6},
266: {"feed_pct": 5.22, "feed_100k": 19.6},
265: {"feed_pct": 5.20, "feed_100k": 19.6},
264: {"feed_pct": 5.19, "feed_100k": 19.7},
263: {"feed_pct": 5.18, "feed_100k": 19.7},
262: {"feed_pct": 5.16, "feed_100k": 19.7},
261: {"feed_pct": 5.15, "feed_100k": 19.7},
260: {"feed_pct": 5.14, "feed_100k": 19.8},
259: {"feed_pct": 5.12, "feed_100k": 19.8},
258: {"feed_pct": 5.11, "feed_100k": 19.8},
257: {"feed_pct": 5.09, "feed_100k": 19.8},
256: {"feed_pct": 5.08, "feed_100k": 19.8},
255: {"feed_pct": 5.07, "feed_100k": 19.9},
254: {"feed_pct": 5.05, "feed_100k": 19.9},
253: {"feed_pct": 5.04, "feed_100k": 19.9},
252: {"feed_pct": 5.03, "feed_100k": 19.9},
251: {"feed_pct": 5.01, "feed_100k": 20.0},
250: {"feed_pct": 5.00, "feed_100k": 20},
249: {"feed_pct": 5.00, "feed_100k": 20.1},
248: {"feed_pct": 5.00, "feed_100k": 20.2},
247: {"feed_pct": 5.00, "feed_100k": 20.2},
246: {"feed_pct": 5.00, "feed_100k": 20.3},
245: {"feed_pct": 5.00, "feed_100k": 20.4},
244: {"feed_pct": 5.00, "feed_100k": 20.5},
243: {"feed_pct": 5.00, "feed_100k": 20.6},
242: {"feed_pct": 5.00, "feed_100k": 20.7},
241: {"feed_pct": 5.00, "feed_100k": 20.7},
240: {"feed_pct": 5.00, "feed_100k": 20.8},
239: {"feed_pct": 5.00, "feed_100k": 20.9},
238: {"feed_pct": 5.00, "feed_100k": 21.0},
237: {"feed_pct": 5.00, "feed_100k": 21.1},
236: {"feed_pct": 4.99, "feed_100k": 21.2},
235: {"feed_pct": 4.99, "feed_100k": 21.2},
234: {"feed_pct": 4.99, "feed_100k": 21.3},
233: {"feed_pct": 4.99, "feed_100k": 21.4},
232: {"feed_pct": 4.99, "feed_100k": 21.5},
231: {"feed_pct": 4.98, "feed_100k": 21.6},
230: {"feed_pct": 4.98, "feed_100k": 21.7},
229: {"feed_pct": 4.98, "feed_100k": 21.7},
228: {"feed_pct": 4.98, "feed_100k": 21.8},
227: {"feed_pct": 4.97, "feed_100k": 21.9},
226: {"feed_pct": 4.97, "feed_100k": 22.0},
225: {"feed_pct": 4.97, "feed_100k": 22.1},
224: {"feed_pct": 4.96, "feed_100k": 22.2},
223: {"feed_pct": 4.96, "feed_100k": 22.2},
222: {"feed_pct": 4.96, "feed_100k": 22.3},
221: {"feed_pct": 4.95, "feed_100k": 22.4},
220: {"feed_pct": 4.95, "feed_100k": 22.5},
219: {"feed_pct": 4.94, "feed_100k": 22.6},
218: {"feed_pct": 4.94, "feed_100k": 22.7},
217: {"feed_pct": 4.93, "feed_100k": 22.7},
216: {"feed_pct": 4.93, "feed_100k": 22.8},
215: {"feed_pct": 4.92, "feed_100k": 22.9},
214: {"feed_pct": 4.92, "feed_100k": 23.0},
213: {"feed_pct": 4.91, "feed_100k": 23.1},
212: {"feed_pct": 4.91, "feed_100k": 23.2},
211: {"feed_pct": 4.90, "feed_100k": 23.2},
210: {"feed_pct": 4.90, "feed_100k": 23.3},
209: {"feed_pct": 4.89, "feed_100k": 23.4},
208: {"feed_pct": 4.89, "feed_100k": 23.5},
207: {"feed_pct": 4.88, "feed_100k": 23.6},
206: {"feed_pct": 4.87, "feed_100k": 23.7},
205: {"feed_pct": 4.87, "feed_100k": 23.7},
204: {"feed_pct": 4.86, "feed_100k": 23.8},
203: {"feed_pct": 4.85, "feed_100k": 23.9},
202: {"feed_pct": 4.84, "feed_100k": 24.0},
201: {"feed_pct": 4.84, "feed_100k": 24.1},
200: {"feed_pct": 4.81, "feed_100k": 24.1},
199: {"feed_pct": 4.81, "feed_100k": 24.2},
198: {"feed_pct": 4.81, "feed_100k": 24.3},
197: {"feed_pct": 4.80, "feed_100k": 24.4},
196: {"feed_pct": 4.79, "feed_100k": 24.5},
195: {"feed_pct": 4.79, "feed_100k": 24.6},
194: {"feed_pct": 4.78, "feed_100k": 24.6},
193: {"feed_pct": 4.77, "feed_100k": 24.7},
192: {"feed_pct": 4.77, "feed_100k": 24.8},
191: {"feed_pct": 4.76, "feed_100k": 24.9},
190: {"feed_pct": 4.75, "feed_100k": 25.0},
189: {"feed_pct": 4.74, "feed_100k": 25.1},
188: {"feed_pct": 4.73, "feed_100k": 25.2},
187: {"feed_pct": 4.73, "feed_100k": 25.3},
186: {"feed_pct": 4.72, "feed_100k": 25.4},
185: {"feed_pct": 4.71, "feed_100k": 25.5},
184: {"feed_pct": 4.70, "feed_100k": 25.5},
183: {"feed_pct": 4.69, "feed_100k": 25.6},
182: {"feed_pct": 4.68, "feed_100k": 25.7},
181: {"feed_pct": 4.67, "feed_100k": 25.8},
180: {"feed_pct": 4.66, "feed_100k": 25.9},
179: {"feed_pct": 4.65, "feed_100k": 26.0},
178: {"feed_pct": 4.64, "feed_100k": 26.1},
177: {"feed_pct": 4.63, "feed_100k": 26.2},
176: {"feed_pct": 4.62, "feed_100k": 26.3},
175: {"feed_pct": 4.61, "feed_100k": 26.4},
174: {"feed_pct": 4.60, "feed_100k": 26.4},
173: {"feed_pct": 4.59, "feed_100k": 26.5},
172: {"feed_pct": 4.58, "feed_100k": 26.6},
171: {"feed_pct": 4.57, "feed_100k": 26.7},
170: {"feed_pct": 4.56, "feed_100k": 26.8},
169: {"feed_pct": 4.54, "feed_100k": 26.9},
168: {"feed_pct": 4.53, "feed_100k": 27.0},
167: {"feed_pct": 4.51, "feed_100k": 27.0},
166: {"feed_pct": 4.48, "feed_100k": 27},
165: {"feed_pct": 4.48, "feed_100k": 27.1},
164: {"feed_pct": 4.47, "feed_100k": 27.3},
163: {"feed_pct": 4.47, "feed_100k": 27.4},
162: {"feed_pct": 4.46, "feed_100k": 27.5},
161: {"feed_pct": 4.46, "feed_100k": 27.7},
160: {"feed_pct": 4.45, "feed_100k": 27.8},
159: {"feed_pct": 4.44, "feed_100k": 28.0},
158: {"feed_pct": 4.44, "feed_100k": 28.1},
157: {"feed_pct": 4.43, "feed_100k": 28.2},
156: {"feed_pct": 4.42, "feed_100k": 28.4},
155: {"feed_pct": 4.42, "feed_100k": 28.5},
154: {"feed_pct": 4.41, "feed_100k": 28.6},
153: {"feed_pct": 4.40, "feed_100k": 28.8},
152: {"feed_pct": 4.39, "feed_100k": 28.9},
151: {"feed_pct": 4.39, "feed_100k": 29.0},
150: {"feed_pct": 4.38, "feed_100k": 29.2},
149: {"feed_pct": 4.37, "feed_100k": 29.3},
148: {"feed_pct": 4.36, "feed_100k": 29.4},
147: {"feed_pct": 4.35, "feed_100k": 29.6},
146: {"feed_pct": 4.34, "feed_100k": 29.7},
145: {"feed_pct": 4.33, "feed_100k": 29.9},
144: {"feed_pct": 4.32, "feed_100k": 30.0},
143: {"feed_pct": 4.29, "feed_100k": 30.0},
142: {"feed_pct": 4.26, "feed_100k": 30},
141: {"feed_pct": 4.25, "feed_100k": 30.1},
140: {"feed_pct": 4.24, "feed_100k": 30.3},
139: {"feed_pct": 4.22, "feed_100k": 30.4},
138: {"feed_pct": 4.21, "feed_100k": 30.5},
137: {"feed_pct": 4.20, "feed_100k": 30.7},
136: {"feed_pct": 4.19, "feed_100k": 30.8},
135: {"feed_pct": 4.17, "feed_100k": 30.9},
134: {"feed_pct": 4.16, "feed_100k": 31.0},
133: {"feed_pct": 4.15, "feed_100k": 31.2},
132: {"feed_pct": 4.13, "feed_100k": 31.3},
131: {"feed_pct": 4.12, "feed_100k": 31.4},
130: {"feed_pct": 4.10, "feed_100k": 31.6},
129: {"feed_pct": 4.09, "feed_100k": 31.7},
128: {"feed_pct": 4.07, "feed_100k": 31.8},
127: {"feed_pct": 4.06, "feed_100k": 32.0},
126: {"feed_pct": 4.03, "feed_100k": 32.0},
125: {"feed_pct": 4.00, "feed_100k": 32},
124: {"feed_pct": 3.99, "feed_100k": 32.2},
123: {"feed_pct": 3.98, "feed_100k": 32.3},
122: {"feed_pct": 3.96, "feed_100k": 32.5},
121: {"feed_pct": 3.95, "feed_100k": 32.7},
120: {"feed_pct": 3.94, "feed_100k": 32.8},
119: {"feed_pct": 3.93, "feed_100k": 33.0},
118: {"feed_pct": 3.91, "feed_100k": 33.2},
117: {"feed_pct": 3.90, "feed_100k": 33.3},
116: {"feed_pct": 3.89, "feed_100k": 33.5},
115: {"feed_pct": 3.87, "feed_100k": 33.7},
114: {"feed_pct": 3.86, "feed_100k": 33.8},
113: {"feed_pct": 3.84, "feed_100k": 34.0},
112: {"feed_pct": 3.81, "feed_100k": 34.0},
111: {"feed_pct": 3.77, "feed_100k": 34},
110: {"feed_pct": 3.78, "feed_100k": 34.3},
109: {"feed_pct": 3.78, "feed_100k": 34.7},
108: {"feed_pct": 3.78, "feed_100k": 35.0},
107: {"feed_pct": 3.78, "feed_100k": 35.3},
106: {"feed_pct": 3.78, "feed_100k": 35.7},
105: {"feed_pct": 3.78, "feed_100k": 36.0},
104: {"feed_pct": 3.78, "feed_100k": 36.3},
103: {"feed_pct": 3.77, "feed_100k": 36.6},
102: {"feed_pct": 3.77, "feed_100k": 37.0},
101: {"feed_pct": 3.77, "feed_100k": 37.3},
100: {"feed_pct": 3.70, "feed_100k": 37},
99: {"feed_pct": 3.70, "feed_100k": 37.4},
98: {"feed_pct": 3.70, "feed_100k": 37.7},
97: {"feed_pct": 3.70, "feed_100k": 38.1},
96: {"feed_pct": 3.69, "feed_100k": 38.5},
95: {"feed_pct": 3.69, "feed_100k": 38.9},
94: {"feed_pct": 3.69, "feed_100k": 39.2},
93: {"feed_pct": 3.68, "feed_100k": 39.6},
92: {"feed_pct": 3.68, "feed_100k": 40.0},
91: {"feed_pct": 3.64, "feed_100k": 40.0},
90: {"feed_pct": 3.60, "feed_100k": 40},
89: {"feed_pct": 3.57, "feed_100k": 40.1},
88: {"feed_pct": 3.54, "feed_100k": 40.3},
87: {"feed_pct": 3.51, "feed_100k": 40.4},
86: {"feed_pct": 3.48, "feed_100k": 40.5},
85: {"feed_pct": 3.45, "feed_100k": 40.6},
84: {"feed_pct": 3.42, "feed_100k": 40.8},
83: {"feed_pct": 3.39, "feed_100k": 40.9},
82: {"feed_pct": 3.36, "feed_100k": 41.0},
81: {"feed_pct": 3.32, "feed_100k": 41.0},
80: {"feed_pct": 3.28, "feed_100k": 41},
79: {"feed_pct": 3.29, "feed_100k": 41.7},
78: {"feed_pct": 3.30, "feed_100k": 42.3},
77: {"feed_pct": 3.31, "feed_100k": 43.0},
76: {"feed_pct": 3.27, "feed_100k": 43},
75: {"feed_pct": 3.26, "feed_100k": 43.5},
74: {"feed_pct": 3.26, "feed_100k": 44.0},
73: {"feed_pct": 3.25, "feed_100k": 44.5},
72: {"feed_pct": 3.24, "feed_100k": 45.0},
71: {"feed_pct": 3.20, "feed_100k": 45},
70: {"feed_pct": 3.19, "feed_100k": 45.5},
69: {"feed_pct": 3.17, "feed_100k": 46.0},
68: {"feed_pct": 3.16, "feed_100k": 46.5},
67: {"feed_pct": 3.15, "feed_100k": 47.0},
66: {"feed_pct": 3.10, "feed_100k": 47},
65: {"feed_pct": 3.06, "feed_100k": 47.0},
64: {"feed_pct": 3.01, "feed_100k": 47.0},
63: {"feed_pct": 2.96, "feed_100k": 47.0},
62: {"feed_pct": 2.91, "feed_100k": 47},
61: {"feed_pct": 2.89, "feed_100k": 47.3},
60: {"feed_pct": 2.86, "feed_100k": 47.7},
59: {"feed_pct": 2.83, "feed_100k": 47.9},
58: {"feed_pct": 2.78, "feed_100k": 48},
57: {"feed_pct": 2.77, "feed_100k": 48.7},
56: {"feed_pct": 2.76, "feed_100k": 49.2},
55: {"feed_pct": 2.75, "feed_100k": 50},
54: {"feed_pct": 2.74, "feed_100k": 50.7},
53: {"feed_pct": 2.71, "feed_100k": 51.2},
52: {"feed_pct": 2.70, "feed_100k": 52},
51: {"feed_pct": 2.65, "feed_100k": 52.0},
50: {"feed_pct": 2.60, "feed_100k": 52},
49: {"feed_pct": 2.56, "feed_100k": 52.3},
48: {"feed_pct": 2.52, "feed_100k": 52.5},
47: {"feed_pct": 2.47, "feed_100k": 52.5},
46: {"feed_pct": 2.42, "feed_100k": 52.7},
45: {"feed_pct": 2.39, "feed_100k": 53},
44: {"feed_pct": 2.33, "feed_100k": 53},
43: {"feed_pct": 2.28, "feed_100k": 53},
42: {"feed_pct": 2.23, "feed_100k": 53},
41: {"feed_pct": 2.17, "feed_100k": 53},
40: {"feed_pct": 2.20, "feed_100k": 55},
39: {"feed_pct": 2.17, "feed_100k": 55.7},
38: {"feed_pct": 2.13, "feed_100k": 56},
37: {"feed_pct": 2.07, "feed_100k": 56},
36: {"feed_pct": 2.05, "feed_100k": 57},
35: {"feed_pct": 2.03, "feed_100k": 58},
34: {"feed_pct": 1.97, "feed_100k": 58},
33: {"feed_pct": 1.98, "feed_100k": 60},


}

# =====================================================
# STORAGE
# =====================================================
# Load once
# ==============================
# LOAD DATA (ONLY ONCE)
# ==============================
if "data" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            st.session_state.data = json.load(f)
    else:
        st.session_state.data = {"farms": {}}

# ==============================
# SAVE FUNCTION
# ==============================
def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(st.session_state.data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ==============================
# SHORTCUT VARIABLE
# ==============================
data = st.session_state.data
# =====================================================
# AUTO-UPGRADE OLD SAMPLING DATA (ADD HERE)
# =====================================================

for farm in data["farms"].values():
    for pond in farm["ponds"].values():

        if "stocking_date" not in pond:
            continue

        stocking_date = datetime.fromisoformat(
            pond["stocking_date"]
        ).date()

        for s in pond.get("sampling_log", []):
            if "DOC" not in s and "sampling_date" in s:
                s["DOC"] = (
                    datetime.fromisoformat(s["sampling_date"]).date()
                    - stocking_date
                ).days + 1

save_data()
from datetime import datetime
from astral import moon

today = datetime.now().date()
moon_phase = moon.phase(today)
# =====================================================
# Moon phase
# =====================================================
def get_moon_name(phase):
    if phase == 0:
        return "New Moon (Amavasya)"
    elif phase == 14:
        return "Full Moon (Pournami)"
    elif phase < 7:
        return "Waxing Crescent"
    elif phase < 14:
        return "Waxing Gibbous"
    elif phase < 21:
        return "Waning Gibbous"
    else:
        return "Waning Crescent"

# =====================================================
# CORE UTILITIES
# =====================================================
def doc_calc(stocking_date, sampling_date):
    sd = datetime.fromisoformat(stocking_date).date()
    return (sampling_date - sd).days + 1

def nearest_count(count):
    return min(REFERENCE_FEED_CHART.keys(), key=lambda x: abs(x - count))

# =====================================================
# SAMPLING ENGINE (CORRECTED)
# =====================================================
def sampling_logic(count_input, daily_feed, pond, sampling_date):

    count_slab = nearest_count(count_input)
    chart = REFERENCE_FEED_CHART[count_slab]

    # Correct ABW formula
    abw = 1000 / count_slab

    DOC = doc_calc(pond["stocking_date"], sampling_date)

    # Survival calculation
    
    current_survival = (daily_feed / chart["feed_100k"]) * 100000
    biomass = (current_survival * abw) / 1000
    present_numbers= (biomass/abw)*1000
      #survival_pct = (present_numbers / pond["initial_stock"]) * 100
    survival_pct = (present_numbers / pond["initial_stock"]) * 100
    excess_feed_flag = False
    excess_feed_qty = 0
    if survival_pct > 100:
        excess_feed_flag = True
    
    # Calculate theoretical max feed based on 100% survival
    max_feed_allowed = chart["feed_100k"] * (pond["initial_stock"] / 100000)
    excess_feed_qty = daily_feed - max_feed_allowed
    
    #survival_pct = 100  # Cap survival
   
    #expected_biomass = (pond["initial_stock"] * abw) / 1000

    record = {
        "sampling_date": sampling_date.isoformat(),
        "DOC": DOC,
        "count": count_slab,
        "abw": round(abw,2),
        "biomass": round(biomass,1),
       # "expected_biomass": round(expected_biomass,1),
        "survival": round(survival_pct,2),
        #"feed_pct": chart["feed_pct"],
        "present_numbers": round(present_numbers,1),
        #"excess_feed_flag": excess_feed_flag,
        "possible_excess_feed_kg": round(excess_feed_qty,2) if excess_feed_flag else 0        
    }
    
    if present_numbers > pond["initial_stock"] * 1.05:
        record["stocking_warning"] = "Check initial stocking entry"
    
    # Weekly metrics
    if pond["sampling_log"]:
        last = pond["sampling_log"][-1]
        gap = DOC - last["DOC"]

        if gap > 0:
            weight_gain = abw - last["abw"]
            biomass_gain = biomass - last["biomass"]
            survival_change = survival_pct - last["survival"]

            feed_used = sum(f["feed"] for f in pond["feed_log"])

            record.update({
                "weekly_growth": round(weight_gain*(7/gap),2),
                "weekly_ADG": round(weight_gain/gap,3),
                "weekly_biomass": round(biomass_gain*(7/gap),1),
                "weekly_survival": round(survival_change,2),
                "weekly_FCR": round(feed_used/biomass_gain,2) if biomass_gain>0 else None
            })

    return record

# ===============================================
# FEED TRAY LOGIC
# ===============================================
def feed_tray_logic(abw, last_feed, tray_left, consumed_time):

    if abw < 5:
        tray_feed = 5
        check_time = 120
    elif abw <= 10:
        tray_feed = 10
        check_time = 90
    elif abw > 25:
        tray_feed = 12
        check_time = 90
    else:
        tray_feed = 10
        check_time = 90

    next_feed = last_feed
    decision = "Maintain feed"

    if tray_left >= 10:
        next_feed -= 1
        decision = "Reduce 1 kg"
    elif tray_left == 5:
        decision = "Maintain feed"
    elif tray_left <= 0:
        next_feed += 1
        decision = "Increase 1 kg"
        if consumed_time <= 30:
            next_feed += 1
            decision = "Increase 2 kg (Strong response)"

    return {
        "tray_feed_g_per_kg": tray_feed,
        "check_time_minutes": check_time,
        "next_feed": max(next_feed,0),
        "decision": decision
    }

st.title("🦐 Shrimp Farm Weather & Feeding Logic")

location = st.text_input("Enter Farm Location", "Chennai")

from geopy.geocoders import Nominatim

if location:

    geolocator = Nominatim(user_agent="shrimp_app")
    location_obj = geolocator.geocode(location)

    if not location_obj:
        st.error("Location not found (try nearby town) or check the spelling")
        st.stop()

    # ✅ Use Nominatim coordinates
    lat = location_obj.latitude
    lon = location_obj.longitude

    st.success(f"Coordinates: {round(lat,4)}, {round(lon,4)}")

    # ----------------------
    # Weather Forecast (No Geocoding Here)
    # ----------------------
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relativehumidity_2m,precipitation,windspeed_10m,pressure_msl",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }

    weather = requests.get(weather_url, params=weather_params, timeout=10).json()
    # ----------------------
    # Extract Current Data
    # ----------------------
    current_temp = weather["current_weather"]["temperature"]
    current_wind = weather["current_weather"]["windspeed"]

    st.subheader("Current Conditions")
    st.write("Temperature:", round(current_temp, 1), "°C")
    st.write("Wind Speed:", round(current_wind, 1), "km/h")

    # ----------------------
    # Rain Forecast (Next 24 hrs)
    # ----------------------
    hourly_df = pd.DataFrame({
        "time": weather["hourly"]["time"],
        "temperature": weather["hourly"]["temperature_2m"],
        "rain": weather["hourly"]["precipitation"]
    })

    next_24_rain = hourly_df["rain"][:24].sum()

    # ----------------------
    # Feeding Logic Engine (Current)
    # ----------------------
    st.subheader("Feeding Recommendation")

    if current_temp > 34:
        st.warning("🔥 High heat → Reduce feed by 15%")
    elif current_temp < 26:
        st.warning("❄ Low temperature → Reduce feed by 25%")
    elif next_24_rain > 20:
        st.warning("🌧 Heavy rain forecast → Reduce feed by 20% before rain")
    elif current_wind > 20:
        st.success("💨 Good wind mixing → Normal feeding")
    else:
        st.success("✅ Normal feeding schedule")

    # ----------------------
    # Daily Forecast
    # ----------------------
    daily_df = pd.DataFrame({
        "Date": weather["daily"]["time"],
        "Max_temp": weather["daily"]["temperature_2m_max"],
        "Min_temp": weather["daily"]["temperature_2m_min"],
        "Rain_total": weather["daily"]["precipitation_sum"]
    })

    # Format date
    daily_df["Date"] = pd.to_datetime(daily_df["Date"]).dt.date

    # Round decimals
    daily_df = daily_df.round({
        "Max_temp": 1,
        "Min_temp": 1,
        "Rain_total": 1
    })

    # ----------------------
    # Feeding Logic (Daily)
    # ----------------------
    def feeding_decision(row):
        if row["Max_temp"] > 34:
            return "Increase Feed"
        elif row["Min_temp"] < 24:
            return "Reduce Feed"
        elif row["Rain_total"] > 20:
            return "Reduce Feed"
        elif 28 <= row["Max_temp"] <= 32 and row["Rain_total"] == 0:
            return "Increase Feed"
        else:
            return "Normal Feeding"

    daily_df["Feeding_Decision"] = daily_df.apply(feeding_decision, axis=1)

    # ----------------------
    # Coloring Function
    # ----------------------
    def color_feed(val):
        if val == "Reduce Feed":
            return "background-color: #ffcccc"
        elif val == "Increase Feed":
            return "background-color: #ccffcc"
        else:
            return ""

    # Style Table
    styled_df = (
        daily_df.style
        .format({
            "Max_temp": "{:.1f}",
            "Min_temp": "{:.1f}",
            "Rain_total": "{:.1f}"
        })
        .applymap(color_feed, subset=["Feeding_Decision"])
    )

    st.subheader("7-Day Forecast with Feeding Decision")
    st.table(styled_df)
# =====================================================
# Lunar tide
# =====================================================
        
show_lunar_tide = st.checkbox("Show Lunar & Tide Information")
if show_lunar_tide:

    st.subheader("🌕 Lunar Information")

    phase_name = get_moon_name(moon_phase)
    st.write("Today's Moon Phase:", phase_name)

    if "Full Moon" in phase_name:
        st.info("Molting activity may increase. Monitor feed trays carefully.")
    elif "New Moon" in phase_name:
        st.warning("Feeding response may reduce. Observe shrimp behavior.")

# =====================================================
# Tide
# =====================================================       
#show_tide = st.checkbox("Show High & Low Tide Information")
#if show_tide:

#    st.subheader("🌊 High & Low Tide Information")

#    tide_url = "https://marine-api.open-meteo.com/v1/marine"

#    tide_params = {
#        "latitude": lat,
#        "longitude": lon,
#        "hourly": "sea_level_height",
#        "timezone": "auto"
#    }

#    tide_response = requests.get(tide_url, params=tide_params)
#    tide_data = tide_response.json()

#    if "hourly" in tide_data:

#        tide_df = pd.DataFrame({
#            "time": tide_data["hourly"]["time"],
#            "sea_level": tide_data["hourly"]["sea_level_height"]
#        })

#        # Convert time column to datetime
#        tide_df["time"] = pd.to_datetime(tide_df["time"])

#        # Take only next 24 hours
#        next_24 = tide_df.head(24)

#        # Detect High & Low
#       high_tide = next_24.loc[next_24["sea_level"].idxmax()]
#        low_tide = next_24.loc[next_24["sea_level"].idxmin()]

#        st.success(f"🌊 High Tide: {high_tide['time']}  |  Level: {round(high_tide['sea_level'],2)} m")
#       st.warning(f"🌊 Low Tide: {low_tide['time']}  |  Level: {round(low_tide['sea_level'],2)} m")
#
#    else:
#        st.error("Tide data not available for this location.")
# =====================================================
# STREAMLIT UI
# =====================================================
st.set_page_config("Pocket Technician", layout="wide")
st.title("🦐 Pocket Technician")

farm_name = st.sidebar.text_input("Farm Name")
if farm_name:
    data["farms"].setdefault(farm_name, {"ponds": {}})

pond_name = st.sidebar.text_input("Pond Name")
pond = None

if farm_name and pond_name:
    ponds = data["farms"][farm_name]["ponds"]

    ponds.setdefault(
        pond_name,
        {
            "initial_stock": 0,
            "area": 0,
            "depth": 0,
            "stocking_date": str(date.today()),
            "feed_log": [],
            "sampling_log": []
        }
    )

    pond = ponds[pond_name]

    # ===== SAFE BACKWARD COMPATIBILITY =====
    pond.setdefault("initial_stock", 0)
    pond.setdefault("area", 0)
    pond.setdefault("depth", 0)
    pond.setdefault("stocking_date", str(date.today()))
    pond.setdefault("feed_log", [])
    pond.setdefault("sampling_log", [])


if pond is None:
    st.stop()

# Pond Inputs
pond["initial_stock"] = st.number_input("Initial Stock", value=pond["initial_stock"])
pond["area"] = st.number_input("Pond Area (m2)", value=pond["area"])
pond["depth"] = st.number_input("Average Depth (m)", value=pond["depth"])
pond["stocking_date"] = st.date_input(
    "Stocking Date",
    value=datetime.fromisoformat(pond["stocking_date"]).date()
).isoformat()

volume = pond["area"] * pond["depth"]
st.write(f"Pond Volume: {volume} m³")

save_data()

# Feed
daily_feed = st.number_input("Feed Given Today (kg)", 0.0)
if st.button("Save Feed"):
    pond["feed_log"].append({"date": str(date.today()), "feed": daily_feed})
    save_data()

# Sampling
count_input = st.number_input("Enter Count (count per kg)", min_value=1)
sampling_date = st.date_input("Sampling Date", value=date.today())

#if st.button("Run Sampling"):
#    record = sampling_logic(count_input, daily_feed, pond, sampling_date)
#    #report_df = pd.DataFrame(record.items(), columns=["Metric", "Value"])
#    st.subheader("Sampling Report")
#    report_df = pd.DataFrame(record.items(), columns=["Metric", "Value"])
#    report_df = report_df.reset_index(drop=True)
#    st.table(report_df)
#    pond["sampling_log"].append(record)
#    save_data(data)
#    #st.json(record)
if st.button("Run Sampling"):

    record = sampling_logic(count_input, daily_feed, pond, sampling_date)

    # Store temporarily (NOT saved yet)
    st.session_state["pending_sampling"] = record

    st.success("Sampling calculated. Review before saving.")

    # Show preview table
    preview_df = pd.DataFrame(record.items(), columns=["Metric", "Value"])

    preview_df["Value"] = preview_df["Value"].apply(
    lambda x: f"{x:.2f}" if isinstance(x, float) else x
)

    st.table(preview_df.set_index("Metric"))
   
if "pending_sampling" in st.session_state:

    if st.button("💾 Save Sampling Record"):

        pond["sampling_log"].append(st.session_state["pending_sampling"])

        st.success("Sampling saved successfully!")

        # Clear temporary data
        del st.session_state["pending_sampling"]
# Feed Tray 
    st.subheader("Feed Tray Calculation")

    if pond["sampling_log"]:
        last_abw = pond["sampling_log"][-1]["abw"]

    last_feed = st.number_input("Last Feed Given (kg)", value=10.0)
    tray_left = st.number_input("Feed Left on Tray (g)", value=5.0)
    consumed_time = st.number_input("Consumed Time (minutes)", value=60)

    if st.button("Calculate Feed Tray Decision"):
        result = feed_tray_logic(last_abw, last_feed, tray_left, consumed_time)
        st.json(result)


# Graph
if pond["sampling_log"]:
    df = pd.DataFrame(pond["sampling_log"])

    # ===== SAFE DOC CREATION FOR OLD DATA =====
    if "DOC" not in df.columns:
        stocking_date = datetime.fromisoformat(pond["stocking_date"]).date()

        df["DOC"] = df["sampling_date"].apply(
            lambda x: (datetime.fromisoformat(x).date() - stocking_date).days + 1
        )

        # Save upgraded data permanently
        pond["sampling_log"] = df.to_dict("records")
        save_data()
        
    st.subheader("📈Growth Curve")
    fig, ax = plt.subplots()
    ax.plot(df["DOC"], df["abw"], marker="o")
    ax.set_xlabel("DOC")
    ax.set_ylabel("ABW (g)")
    st.pyplot(fig)


# Profit per m3
if len(pond["sampling_log"]) >= 2:
    last = pond["sampling_log"][-1]
    fcr = last.get("weekly_FCR")
    if fcr:
        feed_cost = 90
        shrimp_price = 320
        biomass = last["biomass"]

        profit = (biomass*shrimp_price) - (biomass*fcr*feed_cost)
        profit_m3 = profit / volume if volume>0 else 0

        st.subheader("Profit Analysis")
        st.metric("Total Profit", round(profit,0))
        st.metric("Profit per m³", round(profit_m3,2))

# Excel Export
#if st.button("Export Excel (Pond Wise)"):
 #   df = pd.DataFrame(pond["sampling_log"])
  #  file_name = f"{pond_name}_sampling_data.xlsx"
   # df.to_excel(file_name, index=False)
    #st.success("Excel file saved")
 # =====================================================
# MORTALITY CURVE
# =====================================================

st.subheader("📉 Mortality Curve")

if pond["sampling_log"]:
    df = pd.DataFrame(pond["sampling_log"])
    df["mortality_pct"] = 100 - df["survival_pct"]

    fig, ax = plt.subplots()
    ax.plot(df["DOC"], df["mortality_pct"], marker="o", color="red")
    ax.set_xlabel("DOC")
    ax.set_ylabel("Mortality (%)")
    ax.set_title("Mortality Trend")
    st.pyplot(fig)
# =====================================================
# FEED EFFICIENCY TREND
# =====================================================

#st.subheader("📊 Feed Efficiency Trend (Weekly FCR)")

#if pond["sampling_log"]:
 #   df = pd.DataFrame(pond["sampling_log"])

  #  if "weekly_fcr" in df.columns:
   #     df_fcr = df.dropna(subset=["weekly_fcr"])

    #    if not df_fcr.empty:
     #       fig, ax = plt.subplots()
      #      ax.plot(df_fcr["DOC"], df_fcr["weekly_fcr"], marker="o")
       #     ax.set_xlabel("DOC")
        #    ax.set_ylabel("Weekly FCR")
         #   ax.set_title("Feed Efficiency Trend")
          #  st.pyplot(fig)
       # else:
        #    st.info("Weekly FCR data available from 2nd sampling onwards.")
# =====================================================
# HARVEST READINESS PREDICTOR
# =====================================================

st.subheader("🦐 Harvest Readiness Predictor")

target_size = st.number_input("Target Harvest Size (g)", value=25)

if pond["sampling_log"]:
    latest = pond["sampling_log"][-1]
    current_abw = latest["abw"]
    survival = latest["survival_pct"]
    biomass = latest["biomass"]

    if current_abw >= target_size:
        st.success("✔ Shrimp has reached harvest size")

    else:
        if len(pond["sampling_log"]) >= 2:
            prev = pond["sampling_log"][-2]
            growth_rate = latest["abw"] - prev["abw"]
            if growth_rate > 0:
                days_needed = (target_size - current_abw) / growth_rate
                st.info(f"Estimated {round(days_needed,1)} days to reach target size")
            else:
                st.warning("Growth rate too low to estimate harvest time")

    st.write(f"Current Biomass: {biomass} kg")
    st.write(f"Current Survival: {survival} %")
# =====================================================
# ADVANCED TECHNICIAN PDF EXPORT
# =====================================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

st.subheader("📄 Advanced Technician PDF Report")

if st.button("Generate Advanced PDF Report"):

    if not pond["sampling_log"]:
        st.warning("No sampling data available.")
    else:

        df = pd.DataFrame(pond["sampling_log"])

        # Ensure DOC exists
        if "DOC" not in df.columns:
            stocking_date = datetime.fromisoformat(
                pond["stocking_date"]
            ).date()

            df["DOC"] = df["sampling_date"].apply(
                lambda x: (
                    datetime.fromisoformat(x).date() - stocking_date
                ).days + 1
            )

        # =====================================================
        # CREATE GRAPHS
        # =====================================================

        # Growth graph
        growth_img = "growth_curve.png"
        fig1, ax1 = plt.subplots()
        ax1.plot(df["DOC"], df["abw"], marker="o")
        ax1.set_xlabel("DOC")
        ax1.set_ylabel("ABW (g)")
        ax1.set_title("Growth Curve")
        fig1.savefig(growth_img)
        plt.close(fig1)

        # Mortality graph
        mortality_img = "mortality_curve.png"
        df["mortality_pct"] = 100 - df["survival"]

        fig2, ax2 = plt.subplots()
        ax2.plot(df["DOC"], df["mortality_pct"], marker="o", color="red")
        ax2.set_xlabel("DOC")
        ax2.set_ylabel("Mortality (%)")
        ax2.set_title("Mortality Curve")
        fig2.savefig(mortality_img)
        plt.close(fig2)

        # Feed efficiency graph
        fcr_img = "fcr_curve.png"
        if "weekly_FCR" in df.columns:
            df_fcr = df.dropna(subset=["weekly_FCR"])
            if not df_fcr.empty:
                fig3, ax3 = plt.subplots()
                ax3.plot(df_fcr["DOC"], df_fcr["weekly_FCR"], marker="o")
                ax3.set_xlabel("DOC")
                ax3.set_ylabel("Weekly FCR")
                ax3.set_title("Feed Efficiency Trend")
                fig3.savefig(fcr_img)
                plt.close(fig3)
            else:
                fcr_img = None
        else:
            fcr_img = None

        # =====================================================
        # CALCULATIONS
        # =====================================================

        latest = df.iloc[-1]
        volume = pond["area"] * pond["depth"]

        profit = None
        profit_m3 = None

        if "weekly_FCR" in latest and latest["weekly_FCR"]:
            feed_cost = 90
            shrimp_price = 320
            biomass = latest["biomass"]

            profit = (biomass * shrimp_price) - (biomass * latest["weekly_FCR"] * feed_cost)
            profit_m3 = profit / volume if volume > 0 else 0

        biomass_per_m3 = latest["biomass"] / volume if volume > 0 else 0
        # -------------------------
         # Header Function (Logo Only)
        # -------------------------
    
        def add_logo(canvas, doc):
            logo_path = "pt_logo.png"
            if os.path.exists(logo_path):
                 canvas.drawImage(logo_path, 465,260, width=120, preserveAspectRatio=True, mask='auto')
       
        # =====================================================
        # BUILD PDF
        # =====================================================

        file_path = "Advanced_Technician_Report.pdf"
        doc = SimpleDocTemplate(file_path)
        elements = []

        styles = getSampleStyleSheet()
        elements.append(Paragraph("Pocket Technician Advanced Report", styles["Heading1"]))
        elements.append(Spacer(1, 0.3 * inch))

        # =============================
        # FARM HEADER (Inside PDF)
        # =============================

        header_style = styles["Heading1"]
        normal_style = styles["Normal"]

        elements.append(Paragraph(f"🦐 {farm_name}", header_style))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph(f"Location: {location}", normal_style))
        elements.append(Paragraph(f"Pond: {pond_name}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        # -----------------------------------------------------
        # Sampling Table
        # -----------------------------------------------------
        elements.append(Paragraph("Sampling Summary", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))
        #Count= 1000/current_abw
        sampling_table = [
            ["Sampling Date", "DOC", "ABW", "Count", "Survival %", "Biomass"]
        ]

        for _, row in df.iterrows():
            sampling_table.append([
                row["sampling_date"],
                row["DOC"],
                row["abw"],
                row.get("count", "-"),
                row["survival"],
                row["biomass"]
            ])

        table1 = Table(sampling_table, repeatRows=1)
        table1.setStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ])
        elements.append(table1)
        elements.append(Spacer(1, 0.5 * inch))

        # -----------------------------------------------------
        # Weekly Metrics Table
        # -----------------------------------------------------
        if "weekly_growth" in df.columns:
            elements.append(Paragraph("Weekly Metrics", styles["Heading2"]))
            elements.append(Spacer(1, 0.2 * inch))

            weekly_table = [
                ["DOC", "Weekly Growth", "ADG", "Weekly Biomass", "Weekly Survival", "Weekly FCR"]
            ]

            for _, row in df.iterrows():
                if pd.notna(row.get("weekly_growth")):
                    weekly_table.append([
                        row["DOC"],
                        row.get("weekly_growth"),
                        row.get("weekly_ADG"),
                        row.get("weekly_biomass"),
                        row.get("weekly_survival"),
                        row.get("weekly_FCR")
                    ])

            table2 = Table(weekly_table, repeatRows=1)
            table2.setStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ])
            elements.append(table2)
            elements.append(Spacer(1, 0.5 * inch))

        # -----------------------------------------------------
        # Profit Section
        # -----------------------------------------------------
        elements.append(Paragraph("Economic Summary", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        econ_data = [
            ["Pond Volume (m³)", round(volume,2)],
            ["Current Biomass (kg)", latest["biomass"]],
            ["Biomass per m³", round(biomass_per_m3,2)]
        ]

        if profit is not None:
            econ_data.append(["Total Profit", round(profit,0)])
            econ_data.append(["Profit per m³", round(profit_m3,2)])

        table3 = Table(econ_data)
        table3.setStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ])
        elements.append(table3)
        elements.append(Spacer(1, 0.5 * inch))

        # Carrying Capacity Warning
        elements.append(Paragraph("Carrying Capacity Analysis", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        if biomass_per_m3 > 5:
            elements.append(Paragraph("⚠ High biomass load. Risk of oxygen stress.", styles["Normal"]))
        else:
            elements.append(Paragraph("Biomass load within safe range.", styles["Normal"]))

        elements.append(Spacer(1, 0.5 * inch))

        # -----------------------------------------------------
        # Insert Graphs
        # -----------------------------------------------------
        elements.append(Paragraph("Growth Curve", styles["Heading2"]))
        elements.append(Image(growth_img, width=5*inch, height=3*inch))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("Mortality Curve", styles["Heading2"]))
        elements.append(Image(mortality_img, width=5*inch, height=3*inch))
        elements.append(Spacer(1, 0.3 * inch))

        if fcr_img:
            elements.append(Paragraph("Feed Efficiency Trend", styles["Heading2"]))
            elements.append(Image(fcr_img, width=5*inch, height=3*inch))

                # -------------------------
        # Build PDF-used to build a pdf
        # -------------------------
        doc.build(elements, onFirstPage=add_logo, onLaterPages=add_logo)
            

        with open(file_path, "rb") as f:
            st.download_button(
                "Download Advanced Technician Report",
                f,
                file_name="Advanced_Technician_Report.pdf",
                mime="application/pdf"
            )
            
        
st.subheader("📊 Farm Performance Comparison")

if st.button("Generate Multi-Pond Farm Report"):

    file_path = "Farm_Comparison_Report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    summary = []

    # -------------------------
    # Build Performance Summary
    # -------------------------
    for pond_name, pond in data["farms"][farm_name]["ponds"].items():

        if not pond["sampling_log"]:
            continue

        df = pd.DataFrame(pond["sampling_log"])
        latest = df.iloc[-1]

        biomass = latest["biomass"]
        survival = latest["survival"]
        fcr = latest.get("weekly_FCR", 1.5)

        score = (
            survival * 0.4 +
            (1 / fcr) * 100 * 0.3 +
            biomass * 0.3 / 10
        )

        summary.append({
            "Pond": pond_name,
            "Biomass": biomass,
            "Survival": survival,
            "FCR": round(fcr, 2),
            "Score": round(score, 2)
        })

    if not summary:
        st.warning("No pond data available.")
        st.stop()

    summary_df = pd.DataFrame(summary)
    summary_df = summary_df.sort_values("Score", ascending=False)

    # -------------------------
    # Add Grade
    # -------------------------
    def grade(score):
        if score > 85:
            return "A 🟢"
        elif score > 70:
            return "B 🟡"
        else:
            return "C 🔴"

    summary_df["Grade"] = summary_df["Score"].apply(grade)

    # -------------------------
    # Ranking Table
    # -------------------------
    ranking_table = [["Rank", "Pond", "Biomass", "Survival", "FCR", "Score", "Grade"]]

    for i, row in summary_df.reset_index(drop=True).iterrows():
        ranking_table.append([
            i + 1,
            row["Pond"],
            round(row["Biomass"], 2),
            round(row["Survival"], 2),
            row["FCR"],
            row["Score"],
            row["Grade"]
        ])

    # -------------------------
    # Generate Charts
    # -------------------------
    # Growth Chart
    plt.figure()
    for pond_name, pond in data["farms"][farm_name]["ponds"].items():
        if pond["sampling_log"]:
            df = pd.DataFrame(pond["sampling_log"])
            plt.plot(df["DOC"], df["biomass"], label=pond_name)

    plt.xlabel("DOC")
    plt.ylabel("Biomass (kg)")
    plt.title("Pond Biomass Growth Comparison")
    plt.legend()
    plt.tight_layout()
    growth_chart = "growth_multi.png"
    plt.savefig(growth_chart)
    plt.close()

    # Survival Chart
    plt.figure()
    plt.bar(summary_df["Pond"], summary_df["Survival"])
    plt.xticks(rotation=45)
    plt.title("Survival Comparison")
    plt.tight_layout()
    survival_chart = "survival_multi.png"
    plt.savefig(survival_chart)
    plt.close()

    # FCR Chart
    plt.figure()
    plt.bar(summary_df["Pond"], summary_df["FCR"])
    plt.xticks(rotation=45)
    plt.title("Feed Conversion Ratio Comparison")
    plt.tight_layout()
    fcr_chart = "fcr_multi.png"
    plt.savefig(fcr_chart)
    plt.close()

    # -------------------------
    # Header Function (Logo Only)
    # -------------------------
    def add_logo(canvas, doc):
        logo_path = "pt_logo.png"
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 465,260, width=120, preserveAspectRatio=True, mask='auto')

    # -------------------------
    # Build PDF Content
    # -------------------------
    farm_info = data["farms"][farm_name]
    location = farm_info.get("location", "Not Provided")

    elements.append(Paragraph(f"Location: {location}", styles["Normal"]))
    elements.append(Paragraph("🦐 Farm Multi-Pond Performance Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Farm: {farm_name}", styles["Normal"]))
    #elements.append(Paragraph(f"Location: {data['farms'][farm_name]['location']}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
    elements.append(PageBreak())

    # Ranking
    elements.append(Paragraph("🏆 Pond Ranking", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    table = Table(ranking_table, repeatRows=1)
    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    elements.append(table)
    elements.append(PageBreak())

    # Growth
    elements.append(Paragraph("📈 Growth Comparison", styles["Heading2"]))
    elements.append(Image(growth_chart, width=6 * inch, height=3.5 * inch))
    elements.append(PageBreak())

    # Survival
    elements.append(Paragraph("🌱 Survival Comparison", styles["Heading2"]))
    elements.append(Image(survival_chart, width=6 * inch, height=3.5 * inch))
    elements.append(PageBreak())

    # FCR
    elements.append(Paragraph("📊 Feed Efficiency Comparison", styles["Heading2"]))
    elements.append(Image(fcr_chart, width=6 * inch, height=3.5 * inch))

    # -------------------------
    # Build PDF
    # -------------------------
    doc.build(elements, onFirstPage=add_logo, onLaterPages=add_logo)

    # -------------------------
    # Download Button
    # -------------------------
    with open(file_path, "rb") as f:
        st.download_button(
            "📥 Download Farm Comparison Report",
            f,
            file_name="Farm_Comparison_Report.pdf",
            mime="application/pdf"
        )

    st.success("Report generated successfully!")

