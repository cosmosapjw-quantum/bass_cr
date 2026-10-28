vars={aa,bb,ab,ah,bh};
con=aa>=0&&bb>=0&&ab>=0&&ah>=0&&bh>=0&&2aa+ab+ah<=3&&2bb+ab+bh<=1&&ah+bh<=1;
dd=aa+bb+ab+ah+bh;cc=ab+ah+bh;
objectives={dd,cc,2dd-cc,cc-dd,-dd,-cc};
maxima=Table[First[Maximize[{obj,con},vars,Reals]],{obj,objectives}];
vv={{0,0,0,0,0},{3/2,1/2,0,0,0},{1,1/2,0,1,0},{1/2,0,1,1,0},{0,0,1,1,0}};
coords=({dd,cc}/.Thread[vars->#])&/@vv;
valid=And@@(TrueQ[con/.Thread[vars->#]]&/@vv);
<|"maxima"->maxima,"expectedMaxima"->{5/2,2,4,0,0,0},"maximaPass"->(maxima=={5/2,2,4,0,0,0}),"vertexCoordinates"->coords,"allVertexFeasible"->valid,"outsideSameBinFacet"->(2*1-0<=1),"method"->"Exact rational linear optimization; nonnegative singleton slack eliminated"|>
