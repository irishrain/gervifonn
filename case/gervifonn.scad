 $fa=0.25; // default minimum facet angle is now 0.5
 $fs=0.25; 

wall=2.4;
cdwidth=142;
cdheight=125;
cddepth=10;
cdangle=15;
basewidth=cdwidth+8;
baseheight=35;
basedepth=cdwidth;
supportstrength=baseheight*sin(cdangle);
supportheight=0.7*cdheight+baseheight/cos(cdangle);
camerawidth=25;
cameraheight=24;
cameraoffset=20;
camerastrength=7;
cameracable=17;
lensr=3.5;
lenspos=12.5;
panelangle=40;
panelsize=30;

buttonr=6;
dialr=3.5;
dialcylr=17/2;
dialcylh=17;

displaywidth=79;
displayheight=52;

piheight=24;
piholer=1.3;
pisupr=2.5;
pioffsetx=-2;
pioffsety=-2;
piholedistx=60.7-2*piholer;
piholedisty=51.5-2*piholer;
piholedistr=2.2+piholer;

piholderheight=baseheight-wall-piheight;

cabler=2.5;

nut_r=3.15; //Radius aussenkreis um Mutter
screw_r=1.55; //Radius Schraube
screwhead_r=3.05; //Radius Schraubenkopf


module cd() {
cdoffset=sin(cdangle)*cddepth*2;
translate([4,0,-cdoffset]){rotate([cdangle,0,0]){cube([cdwidth,cddepth,cdheight]);}}
    
}

module cd_angled() {
cdoffset=sin(cdangle)*cddepth*2;
translate([-1,0,-cdoffset]){rotate([cdangle,0,0]){cube([basewidth+2,cddepth*2,cdheight]);}}
}




module base() {
    translate([0,0,-baseheight]){
        cube([basewidth,basedepth,baseheight]);
        }
    
    }
module innerbase() {
    translate([wall,wall,-baseheight+wall]){
        difference() {
        cube([basewidth-2*wall,basedepth-2*wall,baseheight-2*wall]);
        translate([0,0,baseheight-2*wall-2*wall]) cube([basewidth-2*wall,2*cddepth,2*wall]);    
        }
    }
    }    
module cdsupport(){
    translate([0,0,-baseheight]){
    rotate([cdangle,0,0]){
 cube([basewidth,supportstrength,supportheight]);
}    }}
   
   
module camera(){
    translate([0.5*(basewidth-camerawidth)-wall,basedepth-camerastrength-2*wall,0]){
    cube([camerawidth+2*wall,camerastrength+2*wall,cameraheight+cameraoffset+2*wall]);
}}


module innercamera(){
    translate([0.5*(basewidth-camerawidth),basedepth-camerastrength-wall,cameraoffset+wall]){
    cube([camerawidth,camerastrength,cameraheight]);
}
  translate([0.5*(basewidth-cameracable),basedepth-camerastrength-wall,-2*wall]){
    cube([cameracable,camerastrength,cameraoffset+4*wall]);
}
   translate([0.5*basewidth,basedepth-camerastrength-3*wall,cameraoffset+wall+cameraheight-lenspos]){
    rotate([-90,0,0]){cylinder(h=3*wall,r=lensr);}}
}




module panel(){
    paneldepth=panelsize*cos(panelangle);
    translate([0,basedepth,0]){difference()
    { translate([0,0,-baseheight]){cube([basewidth,paneldepth,baseheight]);}
       translate([-1,0,0]){rotate([-panelangle,0,0]){cube([basewidth+2,panelsize,paneldepth+1]);}}
    }
}
}

module innerpanel(){
    paneldepth=panelsize*cos(panelangle);
    translate([0,basedepth,0]){difference()
    { translate([wall,-2*wall,-baseheight+wall]){cube([basewidth-2*wall,paneldepth+wall,baseheight-2*wall]);}
       translate([0,0,-wall]){rotate([-panelangle,0,0]){cube([basewidth,panelsize,paneldepth+1]);}}
    }
}
}



module buttons()
{
   dialcenter=0.25*(basewidth-(camerawidth+2*wall));
   buttonzero=0.5*basewidth+wall+0.5*camerawidth;
   buttonoffset=0.3333*(basewidth-buttonzero-wall); 
   translate([0,basedepth,0]){rotate([-panelangle,0,0]){
   translate([dialcenter,0.5*panelsize,-wall]){cylinder(h=2*wall, r=dialr);
       };
       %translate([dialcenter,0.5*panelsize,+wall]){cylinder(h=dialcylh, r=dialcylr);};
   translate([buttonzero+0.5*buttonoffset,0.5*panelsize,-wall]){cylinder(h=2*wall, r=buttonr);
       };
   translate([buttonzero+1.5*buttonoffset,0.5*panelsize,-wall]){cylinder(h=2*wall, r=buttonr);
       };
       translate([buttonzero+2.5*buttonoffset,0.5*panelsize,-wall]){cylinder(h=2*wall, r=buttonr);
       };   
  } }
}


module cablehole()
{
 translate([0.5*basewidth,-50,-0.25*baseheight]){rotate([-90,0,0]){cylinder(h=100,r=cabler);}}
translate([0.5*basewidth,-50,-0.75*baseheight]){rotate([-90,0,0]){cylinder(h=100,r=cabler);}}    
}

module holder() {
    difference(){
        cylinder(h=piholderheight-0.5*wall,r=pisupr);
        translate([0,0,wall]){cylinder(h=baseheight-wall-piheight,r=piholer-0.25);
        }}
    
    }
module piholder(){
   
   yoffset=0.5*(basedepth-camerastrength-2*wall-displayheight);
   xoffset=0.5*(basewidth-displaywidth);
translate([xoffset+pioffsetx+piholedistr,yoffset+pioffsety+piholedistr,-baseheight+0.5*wall]){holder();}
    translate([xoffset+pioffsetx+piholedistr+piholedistx,yoffset+pioffsety+piholedistr,-baseheight+0.5*wall]){holder();}
    translate([xoffset+pioffsetx+piholedistr,yoffset+pioffsety+piholedistr+piholedisty,-baseheight+0.5*wall]){holder();}
    translate([xoffset+pioffsetx+piholedistr+piholedistx,yoffset+pioffsety+piholedistr+piholedisty,-baseheight+0.5*wall]){holder();}
}

module display()
{
    translate([0.5*(basewidth-displaywidth),0.5*(basedepth-camerastrength-2*wall-displayheight),-baseheight+wall]){cube([displaywidth,displayheight,baseheight]);}
}

module screwholders()
{
    translate([0.5*wall,nut_r+3*wall,-0.5*baseheight]){
   rotate([0,90,0]){cylinder(r=nut_r+wall,h=basewidth-wall);}} 
    translate([0.5*wall,basedepth-nut_r-4*wall,-0.5*baseheight]){
   rotate([0,90,0]){cylinder(r=nut_r+wall,h=basewidth-wall);}}
   
   translate([nut_r+3*wall,2*nut_r+6*wall,-baseheight+0.5*wall]){
   cylinder(r=nut_r+wall,h=baseheight-wall);}

translate([nut_r+3*wall,basedepth-2*nut_r-7*wall,-baseheight+0.5*wall]){
   cylinder(r=nut_r+wall,h=baseheight-wall);}   

   translate([basewidth-nut_r-3*wall,2*nut_r+6*wall,-baseheight+0.5*wall]){
   cylinder(r=nut_r+wall,h=baseheight-wall);}
   
   
translate([basewidth-nut_r-3*wall,basedepth-2*nut_r-7*wall,-baseheight+0.5*wall]){
   cylinder(r=nut_r+wall,h=baseheight-wall);}

translate([0.5*basewidth-4*wall,-0.1,-0.5*baseheight-wall/2]) cube([8*wall,2.5*wall,wall]);

translate([0.5*basewidth-4*wall,basedepth-nut_r-4.5*wall,-wall+0.1-0.5*baseheight]) cube([8*wall,wall,0.5*baseheight]);   
   
}


module screwholes()
{
    translate([0.5*basewidth-10,nut_r+3*wall,-0.5*baseheight]){
   rotate([0,-90,0]){cylinder(r=nut_r,h=basewidth, $fn=6);}}
    translate([0,nut_r+3*wall,-0.5*baseheight]){
   rotate([0,90,0]){cylinder(r=screw_r,h=basewidth);}}
   translate([0.5*basewidth+10,nut_r+3*wall,-0.5*baseheight]){
   rotate([0,90,0]){cylinder(r=screwhead_r,h=basewidth);}}
   
   translate([0.5*basewidth-10,basedepth-nut_r-4*wall,-0.5*baseheight]){
   rotate([0,-90,0]){cylinder(r=nut_r,h=basewidth, $fn=6);}}
    translate([0,basedepth-nut_r-4*wall,-0.5*baseheight]){
   rotate([0,90,0]){cylinder(r=screw_r,h=basewidth);}}
   translate([0.5*basewidth+10,basedepth-nut_r-4*wall,-0.5*baseheight]){
   rotate([0,90,0]){cylinder(r=screwhead_r,h=basewidth);}}
   
     
   translate([nut_r+3*wall,2*nut_r+6*wall,-baseheight+piholderheight+wall]){
   cylinder(r=nut_r,h=baseheight, $fn=6);}
   translate([nut_r+3*wall,2*nut_r+6*wall,-2*baseheight+piholderheight-wall]){
   cylinder(r=screwhead_r,h=baseheight);}
   translate([nut_r+3*wall,2*nut_r+6*wall,-baseheight]){
   cylinder(r=screw_r,h=baseheight);}



   translate([nut_r+3*wall,basedepth-2*nut_r-7*wall,-baseheight+piholderheight+wall]){
   cylinder(r=nut_r,h=baseheight, $fn=6);}
   translate([nut_r+3*wall,basedepth-2*nut_r-7*wall,-2*baseheight+piholderheight-wall]){
   cylinder(r=screwhead_r,h=baseheight);}
   translate([nut_r+3*wall,basedepth-2*nut_r-7*wall,-baseheight]){
   cylinder(r=screw_r,h=baseheight);}


   translate([basewidth-nut_r-3*wall,2*nut_r+6*wall,-baseheight+piholderheight+wall]){
   cylinder(r=nut_r,h=baseheight, $fn=6);}
   translate([basewidth-nut_r-3*wall,2*nut_r+6*wall,-2*baseheight+piholderheight-wall]){
   cylinder(r=screwhead_r,h=baseheight);}
   translate([basewidth-nut_r-3*wall,2*nut_r+6*wall,-baseheight]){
   cylinder(r=screw_r,h=baseheight);}


   translate([basewidth-nut_r-3*wall,basedepth-2*nut_r-7*wall,-baseheight+piholderheight+wall]){
   cylinder(r=nut_r,h=baseheight, $fn=6);}
   translate([basewidth-nut_r-3*wall,basedepth-2*nut_r-7*wall,-2*baseheight+piholderheight-wall]){
   cylinder(r=screwhead_r,h=baseheight);}
   translate([basewidth-nut_r-3*wall,basedepth-2*nut_r-7*wall,-baseheight]){
   cylinder(r=screw_r,h=baseheight);}


}

module lefthalf() {
    translate([0.5*basewidth,-basedepth,-cdheight]){cube([basewidth,3*basedepth,3*cdheight]);};
}

module floorplate() {
    translate([1.5*wall,1.5*wall,-baseheight-piholderheight]){cube([basewidth-3*wall,basedepth-3*wall+15,2*piholderheight+0.01]);}
    
}

module  gervifonn(part=1)
{

if (part==1){
intersection(){
difference(){
union(){
  difference(){ 
    union(){
        base();
        cdsupport();
        camera();
        panel();
        }
cd_angled();
display();
buttons();
innerbase();
innercamera();
innerpanel();
cablehole();        
}
piholder();
screwholders();
}
screwholes();
}
floorplate();
}
}




if (part==2){
intersection(){
    lefthalf();
difference(){
union(){
  difference(){ 
    union(){
        base();
        cdsupport();
        camera();
        panel();
        }
cd_angled();
display();
buttons();
innerbase();
innercamera();
innerpanel();
cablehole();        
}
piholder();
screwholders();
}
screwholes();
floorplate();
}

}
}




if (part==3){
difference(){

difference(){
union(){
  difference(){ 
    union(){
        base();
        cdsupport();
        camera();
        panel();
        }
cd_angled();
display();
buttons();
innerbase();
innercamera();
innerpanel();
cablehole();        
}
piholder();
screwholders();
}
screwholes();
floorplate();
}
    lefthalf();
}
}




}


gervifonn(part=1);
gervifonn(part=2);
gervifonn(part=3);
%cd();
