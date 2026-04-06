# Reference Data Sources for Procedural Building Generation

Comprehensive catalog of open/free datasets, books, and resources containing architectural
floor plans, building layouts, and blueprints.

---

## 1. Open Floor Plan Datasets

### RPLAN Dataset
- **Content**: 80,788 densely annotated rasterized floor plans from the Asian (Chinese) real estate market
- **Format**: 256x256 pixel multi-channel images with room type and structural component annotations
- **Download**: http://staff.ustc.edu.cn/~fuxm/projects/DeepLayout/index.html
- **License**: Research use; redistribution of data is NOT permitted
- **Tools**:
  - [RPLAN-Toolbox](https://github.com/zzilch/RPLAN-Toolbox) - Python toolbox
  - [rplanpy](https://github.com/unaisaralegui/rplanpy) - Python utilities
- **Notes**: Predominantly single-unit apartments with mostly rectangular room shapes. Catalyzed many subsequent works in data-driven layout synthesis.

### CubiCasa5k
- **Content**: 5,000 floor plan images annotated into 80+ floorplan object categories using polygon annotations
- **Format**: Images with dense polygon annotations (SVG-style)
- **Download**: https://github.com/CubiCasa/CubiCasa5k
- **Also on**: [Kaggle](https://www.kaggle.com/datasets/qmarva/cubicasa5k), [Hugging Face](https://huggingface.co/datasets/Claudio9701/cubicasa5k)
- **License**: **CC BY-NC 4.0** (non-commercial use with attribution)
- **Paper**: [arXiv:1904.01920](https://arxiv.org/abs/1904.01920)
- **Derivative**: [CubiGraph5K](https://github.com/luyueheng/CubiGraph5K) - organizational graph representations

### LIFULL HOME'S Dataset
- **Content**: 5.31 million floor plan images (JPG, ~140GB) from Japanese real estate listings, plus rental metadata (fee, area, location, age, structure, facilities)
- **Format**: JPG images + structured metadata
- **Download**: https://www.nii.ac.jp/dsc/idr/en/lifull/
- **License**: Free for academic research only; requires application by a principal investigator at a university or public research institution
- **Notes**: Largest floor plan dataset available but restricted access. Application form required.

### FloorPlanCAD
- **Content**: 15,000+ real-world CAD floor plans ranging from residential to commercial buildings
- **Format**: SVG (vector CAD drawings)
- **Download**: https://floorplancad.github.io/
- **Also on**: [Hugging Face](https://huggingface.co/datasets/Voxel51/FloorPlanCAD)
- **Notes**: Vector format makes it particularly useful for extracting structural geometry.

### Modified Swiss Dwellings (MSD)
- **Content**: 4,167 floor plans of single- and multi-unit building complexes across Switzerland; 18,900+ distinct apartments
- **Format**: Structured data with room polygons and metadata
- **Download**:
  - [Kaggle](https://www.kaggle.com/datasets/caspervanengelenburg/modified-swiss-dwellings)
  - [4TU.ResearchData](https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9)
- **GitHub**: https://github.com/caspervanengelenburg/msd
- **Paper**: ECCV 2024
- **Notes**: Multi-unit focus fills a gap left by RPLAN/LIFULL. Includes building complex layouts.

### Swiss Dwellings (Original)
- **Content**: Large dataset of apartment models with simulation results (viewshed, natural light, traffic noise, centrality, geometric analysis)
- **Download**: https://zenodo.org/records/7070952
- **Also on**: [Kaggle](https://www.kaggle.com/datasets/michaelbryantds/swiss-dwellings-dataset)

### ResPlan (New - 2025)
- **Content**: 17,000 vector-based residential floor plan instances with graph-based room connectivity
- **Format**: Clean vector graphics + graph representations
- **GitHub**: https://github.com/m-agour/ResPlan
- **Paper**: [arXiv:2508.14006](https://arxiv.org/html/2508.14006v1)
- **Notes**: Ranges from standard apartments to complex multi-wing homes. Designed for ML models, virtual environments, and robotic simulators.

### SYNBUILD-3D (New)
- **Content**: 100,000+ 3D building wireframes with corresponding floor plan images
- **Paper**: [OpenReview](https://openreview.net/forum?id=TCSaLeANpN)
- **Notes**: Multi-modal (3D wireframes + 2D plans), validated by building modeling experts. Rich geometric and semantic information.

### MLSTRUCT-FP
- **Content**: Multi-unit floor plan dataset for architectural analysis and recognition
- **GitHub**: https://github.com/MLSTRUCT/MLSTRUCT-FP
- **Paper**: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0926580523003928)

### Other Floor Plan Datasets
- **[VahidAz/Floorplan_dataset](https://github.com/VahidAz/Floorplan_dataset)** - Community-collected floor plan dataset on GitHub
- **[rickkk856/ArchitectureDesign-DataSources](https://github.com/rickkk856/ArchitectureDesign-DataSources)** - Meta-repository listing multiple data sources for architecture and design experiments

---

## 2. Historical Architectural Reference Books (Public Domain)

### Classical Treatises on Archive.org

#### Palladio - The Four Books of Architecture
- https://archive.org/details/gri_33125011115488 (English translation with plates)
- https://archive.org/details/gri_33125011569684 (Another edition)
- https://archive.org/details/andreapalladiosa00pall (Revised and redelineated edition)
- **Content**: Book I covers building materials and the five classical orders (Doric, Ionic, Corinthian, Tuscan, Composite). Book II covers private townhouses and country villas (9 palazzi, 22 villas). Books III-IV cover public buildings, temples, bridges.
- **License**: Public domain
- Also available via [Smithsonian Digital Library](https://library.si.edu/digital-library/book/architecturepal00pall)

#### Vitruvius - De Architectura / On Architecture
- https://archive.org/details/vitruviusonarchi0000vitr (Vitruvius on Architecture)
- https://archive.org/details/vitruvius-on-architecture-loeb (Loeb Classical Library edition, translated by Frank Granger, 816 pages)
- **Content**: Ten books covering city planning, building materials, temples, civil buildings, domestic buildings, floors, stucco, painting, water supply, astronomy, and machines
- **License**: Public domain (original text; translations vary)

### Builder's Guides and Pattern Books on Archive.org

- **[Home Builders Catalog (1928)](https://archive.org/details/HomeBuildersCatalogPlansOfAllTypesOfSmallHomes)** - 618 pages, plans of all types of small homes. Public Domain Mark 1.0.
- **[Modern Home Plans (1950)](https://archive.org/details/ModernHomePlans)** - Ranch houses and residential designs. Public Domain Mark 1.0.
- **[Building Service (House Plans)](https://archive.org/details/BuildingServicehousePlans)** - ~150 pages of house plans, churches, commercial buildings, banks. Public domain.
- **[The Book of 100 Homes (1946)](https://archive.org/details/BrownBlodgettBook100HomesJ0001)** - 100+ home designs and floor plans. Public Domain Mark 1.0.
- **[The American Home Book of House Plans](https://archive.org/details/americanhomebook00unse)** - Historical American house plans.

### Victorian/Georgian Pattern Books (search Archive.org for these titles)
- *Early Victorian House Designs* by William H. Ranlett (1847)
- *Architecture of Country Houses* by Andrew Jackson Downing (1850)
- *Sloan's Victorian Buildings* by Samuel Sloan (1852)
- *Woodward's National Architect* by George E. Woodward (1869) - also published as *A Victorian Housebuilder's Guide*

### Other Public Domain Collections
- **[Library of Congress Architectural Drawings](https://loc.getarchive.net/topics/architectural+drawings)** - 10,722 architectural drawings in the public domain
- **[Library of Congress Floor Plans](https://loc.getarchive.net/topics/floor+plans)** - 566 floor plan images in the public domain
- **[The Public Domain Review - Architecture](https://publicdomainreview.org/collections/all/theme/architecture/)** - Curated collection of public domain architectural works
- **[UK National Archives - Architectural Drawings](https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/architectural-drawings/)** - Research guide for architectural drawings

---

## 3. Open Building Data

### OpenStreetMap Building Data
- **Content**: Global building footprints with tags for building type, height, levels, material, roof shape, and more
- **Building tag reference**: https://wiki.openstreetmap.org/wiki/Key:building
- **How to download**: Export from openstreetmap.org, or use tools like:
  - **OSMnx** (Python) - downloads footprints + street networks + amenities
  - **Overpass API** - query-based extraction
  - **Geofabrik** downloads (pre-packaged regional extracts)
- **OSM Buildings**: https://osmbuildings.org/data/ - 3D building visualization with height data
- **License**: ODbL (Open Database License)
- **Notes**: Coverage and attribute completeness varies greatly by region. Height data often missing.

### US Building Classification Dataset
- **Content**: Residential/non-residential building classification for the entire United States based on OSM footprints
- **Paper**: [Nature Scientific Data](https://www.nature.com/articles/s41597-024-04046-w)
- **License**: Open

### Microsoft Global Building Footprints
- **Content**: 999 million building footprint polygons worldwide, derived from satellite imagery
- **Format**: Line-delimited GeoJSON (gzipped)
- **Download**: https://github.com/microsoft/GlobalMLBuildingFootprints
- **Also via**: Microsoft Planetary Computer
- **License**: ODbL

### Google Open Buildings
- **Content**: 1.8 billion building outlines (Africa, Latin America, Caribbean, South/Southeast Asia)
- **Format**: Gzipped CSV; also available via Google Earth Engine
- **Catalog**: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_open-buildings_v3_polygons
- **License**: CC BY 4.0

### Combined Google-Microsoft Dataset
- **Content**: 2.58 billion building footprints merged from both sources
- **Format**: GeoParquet, FlatGeobuf, PMTiles
- **Download**: https://source.coop/vida/google-microsoft-open-buildings
- **Notes**: Each footprint labeled with source (Google or Microsoft) and confidence score

### OpenBuildingMap
- **Content**: Global building footprints with semantic information (building type classification)
- **Info**: https://gee-community-catalog.org/projects/obm/

---

## 4. BIM/IFC Open Datasets

### BIMData Research Collection
- **Content**: 40 BIM models / 100 IFC files (3.7 GB) covering Architecture and Plumbing
- **GitHub**: https://github.com/bimdata/BIMData-Research-and-Development/blob/master/pages/IFC_FILES.md

### IFC Sample Files
- **Content**: Collection of IFC sample files for software testing
- **GitHub**: https://github.com/youshengCode/IfcSampleFiles

### Kaggle IFC Examples
- **Content**: Building Information Model IFC file examples
- **Download**: https://www.kaggle.com/datasets/claytonmiller/example-ifc-file

### SIMAUD BIM Datasets
- **Content**: BIM models with geometric/semantic aspects + point cloud data from terrestrial laser scanning
- **Info**: https://www.simaud.org/datasets/

### Purdue BIM Data Repository
- **Content**: AEC objects with geometric signatures, labeled
- **Info**: https://purr.purdue.edu/publications/3259/1

### Free IFC Component Libraries
- **[BIMsmith Market](https://market.bimsmith.com/IFC)** - Free IFC files with specifications
- **[Modlar](https://www.modlar.com/search/format/ifc/)** - Free BIM content in IFC and other formats
- **[OSArch Community](https://community.osarch.org/discussion/685/open-free-ifc-repository-for-building-components)** - Open-source architecture community IFC resources

---

## 5. 3D Model Libraries

### Open3dModel
- **Content**: 6,830+ 3D building models
- **Formats**: Blender (.blend), 3ds Max (.max), OBJ, SketchUp (.skp), Cinema 4D (.c4d), Maya, FBX, STL
- **URL**: https://open3dmodel.com/3d-models/building
- **License**: Varies per model

### SketchUp 3D Warehouse
- **Content**: Massive library of architectural elements, furniture, fixtures, vehicles, and complete building projects
- **URL**: https://3dwarehouse.sketchup.com/
- **License**: SketchUp terms; free to use in SketchUp projects

### BlenderKit
- **Content**: Community-driven 3D asset library integrated into Blender
- **Architecture section**: https://www.blenderkit.com/?query=is_free:true+category:architecture
- **Buildings section**: https://www.blenderkit.com/?query=is_free:true+order:-created+category:building
- **License**: Free tier available; some assets require subscription

### Sketchfab
- **Content**: Large platform with architectural 3D models, many free under Creative Commons licenses
- **URL**: https://sketchfab.com/
- **Formats**: Exportable to Blender, Unity, Unreal Engine
- **License**: Many models under CC licenses (CC BY, CC BY-SA, CC0)

### Blender 3D Architect
- **URL**: https://www.blender3darchitect.com/
- **Content**: Resources, tutorials, and assets for architectural work in Blender

### Architizer Free SketchUp Models
- **Content**: 17 iconic architectural buildings fully modeled in SketchUp (free)
- **URL**: https://architizer.com/blog/practice/tools/free-iconic-buildings/

---

## 6. Historical Building Type References

### Medieval Castle Layouts
- **[Great Castles - Floor Plans](https://great-castles.com/floorplans.html)** - Collection of castle floor plans
- **[Exploring Castles - Medieval Castle Layout](https://www.exploring-castles.com/castle_designs/medieval_castle_layout/)** - Detailed breakdown of rooms and areas
- **[Historic European Castles](https://historiceuropeancastles.com/medieval-castle-layout/)** - Castle layout reference
- **[Revisiting History - Castle Parts](https://www.revisitinghistory.com/medieval/castle-parts-and-layouts/)** - Parts and layouts reference

**Typical Castle Components:**
- Exterior: walls, gate, barbicans, portcullis, moat
- Outer bailey: stables, training facilities, outbuildings, exterior courtyard
- Inner castle: keep/donjon, great hall, bed chambers, kitchens, inner courtyard
- Keep interior: basement with water source, great hall, private chambers on upper floors

### Medieval Taverns and Inns
- **[Lost Kingdom - Medieval Inn & Tavern](http://www.lostkingdom.net/medieval-inn-tavern/)** - Detailed layout reference
- **[University of Warwick - World of the Tavern](https://warwick.ac.uk/fac/arts/history/students/modules/hi390/topics/session11/plans/)** - Historical tavern plans
- **[SFF Chronicles - Structure of a Medieval Inn](https://www.sffchronicles.com/threads/548095/)** - Discussion with references
- **[Paths Peculiar - Medieval Fantasy Inn Map](https://www.wistedt.net/2022/04/17/medieval-fantasy-inn-map/)** - Detailed inn maps

**Typical Medieval Inn/Tavern Components:**
- Common room (bar) - usually the largest room
- Multiple small rooms or booths/alcoves (not open plan)
- Forecourt, parlour/best kitchen, pantry, common kitchen
- Cellar, store room, milk room
- Upstairs: guest chambers
- Outbuildings: stable, barn, hogstye, hovels (sheds), boghouse (toilet)

### RPG/Gaming Map Resources
- **[DriveThruRPG - Inns and Taverns Floorplans](https://www.drivethrurpg.com/en/product/16522/Inns-and-Taverns-Floorplans)** - 20 inns + 15 taverns with multiple levels (70+ floorplans total)
- **Pinterest collections** for castle, tavern, and medieval building layouts (search "medieval castle layout", "tavern floor plan")

---

## 7. Summary: Best Picks by Use Case

### For ML/Procedural Generation (Vector Data)
| Dataset | Size | Format | Access |
|---------|------|--------|--------|
| ResPlan | 17,000 | Vector + graphs | Open |
| FloorPlanCAD | 15,000+ | SVG/CAD | Open |
| MSD | 4,167 floor plans | Structured polygons | Open (Kaggle) |
| CubiCasa5k | 5,000 | Annotated images | Open (CC BY-NC 4.0) |
| RPLAN | 80,788 | Raster 256x256 | Restricted redistribution |

### For Building Footprints/Urban Scale
| Source | Size | Coverage |
|--------|------|----------|
| Google+Microsoft Combined | 2.58B footprints | Global |
| OpenStreetMap | Varies | Global (with attributes) |
| US Building Classification | All US buildings | United States |

### For Historical Reference (Public Domain)
- Palladio's Four Books (Archive.org) - Classical/Renaissance
- Vitruvius De Architectura (Archive.org) - Roman/Classical
- Library of Congress (10,722 architectural drawings) - American historical
- 1920s-1950s pattern books (Archive.org) - Early modern residential

### For 3D Assets
- Open3dModel (6,830+ building models, multiple formats)
- SketchUp 3D Warehouse (largest collection)
- BlenderKit (Blender-native, free tier)
- Sketchfab (CC-licensed models)
