select prc.codenscda || prc.codpntvtecda as "psav",
to_char(prc.datcreprc, 'YYYY-MM-DD') || 'T' || to_char(prc.datcreprc,'HH24:MI:SS') || '.000+0100' as "date" ,
decode(clacar.libcla,null,famart.libfam,clacar.libcla) as "classe"
 from prc inner join etpprc on prc.codetp = etpprc.codetp
left join prcrpcsim on prcrpcsim.numinv = prc.numinv
left join prcprt on prcprt.numinv = prc.numinv
left join prt prtsim on prtsim.numser = prcrpcsim.numser
left join art artsim on artsim.gencod = prtsim.gencod
left join famart on artsim.codfam = famart.codfam
left join prt prtprt on prtprt.numser = prcprt.numser
left join art artprt on artprt.gencod = prtprt.gencod
left join mod on mod.codmod = artprt.codmod
left join clacar on clacar.codcla = mod.codcla
where etpprc.codnomprc in (3,5)
