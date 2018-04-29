//Maya ASCII 2018ff07 scene
//Name: waterdrop.ma
//Last modified: Thu, Apr 26, 2018 05:14:04 PM
//Codeset: 1252
requires maya "2018ff07";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201711281015-8e846c9074";
fileInfo "osv" "Microsoft Windows 8 Business Edition, 64-bit  (Build 9200)\n";
createNode transform -n "nurbsCircle1";
	rename -uid "6FD7493C-4987-4BBE-ACDF-3AB414E6DA14";
createNode nurbsCurve -n "nurbsCircleShape1" -p "nurbsCircle1";
	rename -uid "C26CCCAE-434B-20D2-DAAA-6ABAC2E72CAA";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 13 2 no 3
		18 -2 -1 0 1 2 3 3.4581675920000001 3.6714631679999998 4 4.1069210509999996
		 4.2673026790000002 4.5050367900000001 5 6 7 8 9 10
		16
		4.7982373409884725e-17 0.7836116248912246 -0.78361162489122449
		4.1550626846842558e-33 1.1081941875543877 -6.7857323231109122e-17
		-4.7982373409884725e-17 0.78361162489122438 0.78361162489122449
		-6.7857323231109146e-17 5.7448982375248304e-17 1.1081941875543881
		-5.1572004050055789e-17 -0.6420829003406896 0.84223474206542215
		-2.9081009103380436e-17 -0.9184886372153056 0.43923545184622126
		-1.392079395938586e-17 -0.99577313591856875 0.11690325277114008
		-3.5445503858217585e-18 -1.113871087485752 7.7819695132319566e-14
		5.9853809172332845e-18 -1.1138710874856856 -7.7826634026223473e-14
		1.3995384663358963e-17 -0.99577313591856875 -0.11690325277114008
		2.77146118750633e-17 -0.9184886372153056 -0.43923545184622126
		5.1328233696258812e-17 -0.65169405834397509 -0.83825367007035056
		6.7857323231109146e-17 -1.511240500779959e-16 -1.1081941875543881
		4.7982373409884725e-17 0.7836116248912246 -0.78361162489122449
		4.1550626846842558e-33 1.1081941875543877 -6.7857323231109122e-17
		-4.7982373409884725e-17 0.78361162489122438 0.78361162489122449
		;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr -s 4 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :ikSystem;
	setAttr -s 4 ".sol";
// End of waterdrop.ma
