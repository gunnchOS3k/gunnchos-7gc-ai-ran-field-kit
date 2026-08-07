// REPRESENTATIVE_ENCLOSURE — parameterized concept model
// Device: Handheld Hybrid (handheld_hybrid)
// Status: REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING
// Evidence class: MODELED (not MEASURED)

device_id = "handheld_hybrid";
outer_w = 180;
outer_d = 95;
outer_h = 28;
wall = 2.0;
corner_r = 4.0;
tolerance = 0.3;

module outer_shell() {
  difference() {
    cube([outer_w, outer_d, outer_h], center=true);
    cube([outer_w-2*wall, outer_d-2*wall, outer_h-2*wall], center=true);
  }
}

module interference_keepout() {
  // Battery / PCB keepouts for digital interference check
  translate([0, 0, -outer_h/4]) cube([outer_w*0.6, outer_d*0.5, outer_h*0.35], center=true);
}

outer_shell();
%interference_keepout();
