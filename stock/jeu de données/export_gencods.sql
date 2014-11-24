select art.gencod, clacar.codcla, clacar.libcla,famart.codfam, famart.libfam, typpdt.codtyppdt, typpdt.libtyppdt
from
       art inner join mod on mod.codmod = art.codmod
       inner join clacar on mod.codcla = clacar.codcla
       inner join famart on art.codfam = famart.codfam
       inner join typpdt on famart.codtyppdt = typpdt.codtyppdt
where
       famart.codtyppdt in ('KDP', 'KDP_F', 'SIM','SIM_F')       
