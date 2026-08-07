// REPRESENTATIVE_ENCLOSURE — parameterized concept model
// Device: Edge I/O Rings (edge_io_rings)
// Status: REPRESENTATIVE_ENCLOSURE_PHYSICAL_PENDING
// Evidence class: MODELED (not MEASURED)

device_id = "edge_io_rings";
outer_w = 22;
outer_d = 22;
outer_h = 12;
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
