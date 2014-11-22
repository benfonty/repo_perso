select 
  prt.numser as "imei", 
  prt.codlit as "litige", 
  prt.gencod as "gencod", 
  prt.codenscda || prt.codpntvtecda as "psav",
  prt.codmtf as "motif", prt.codeta as "etat", 
  prt.numprc as "bi", 
  to_char(prt.datmaj, 'YYYY-MM-DD') || 'T' || to_char(prt.datmaj,'HH24:MI:SS') || '.000+0100' as "datmaj" ,
  famart.codtyppdt as "type",
  mod.codcla as "classe",
  famart.codfam as "famille"
from prt
     inner join art on art.gencod = prt.gencod
     inner join famart on famart.codfam = art.codfam
     inner join mod on art.codmod = mod.codmod

