<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.10" tiledversion="1.11.2" name="EnemyPaths" tilewidth="64" tileheight="64" tilecount="12" columns="0">
 <grid orientation="orthogonal" width="1" height="1"/>
 <tile id="13">
  <properties>
   <property name="spawn" value="enemy1"/>
  </properties>
  <image source="tilesets/Logic/enemyspawn1.png" width="64" height="64"/>
 </tile>
 <tile id="14">
  <properties>
   <property name="spawn" value="enemy2"/>
  </properties>
  <image source="tilesets/Logic/enemyspawn2.png" width="64" height="64"/>
 </tile>
 <tile id="15">
  <properties>
   <property name="spawn" value="enemy3"/>
  </properties>
  <image source="tilesets/Logic/enemyspawn3.png" width="64" height="64"/>
 </tile>
 <tile id="16">
  <properties>
   <property name="spawn" value="enemy4"/>
  </properties>
  <image source="tilesets/Logic/enemyspawn4.png" width="64" height="64"/>
 </tile>
 <tile id="17">
  <properties>
   <property name="direction" value="up"/>
  </properties>
  <image source="tilesets/Logic/UP.png" width="64" height="64"/>
 </tile>
 <tile id="18">
  <properties>
   <property name="direction" value="left"/>
  </properties>
  <image source="tilesets/Logic/LEFT.png" width="64" height="64"/>
 </tile>
 <tile id="19">
  <properties>
   <property name="direction" value="right"/>
  </properties>
  <image source="tilesets/Logic/RIGHT.png" width="64" height="64"/>
 </tile>
 <tile id="20">
  <properties>
   <property name="direction" value="down"/>
  </properties>
  <image source="tilesets/Logic/DOWN.png" width="64" height="64"/>
 </tile>
 <tile id="21">
  <properties>
   <property name="spawn" value="player"/>
  </properties>
  <image source="tilesets/Logic/playerspawn.png" width="64" height="64"/>
 </tile>
 <tile id="24">
  <properties>
   <property name="interactiontype" value="shop"/>
  </properties>
  <image source="tilesets/Logic/interaction_shop.png" width="64" height="64"/>
 </tile>
 <tile id="25">
  <properties>
   <property name="interactiontype" value="startgame"/>
  </properties>
  <image source="tilesets/Logic/interaction_startgame.png" width="64" height="64"/>
 </tile>
 <tile id="28">
  <properties>
   <property name="interactiontype" value="lobby"/>
  </properties>
  <image source="tilesets/Logic/interaction_lobby.png" width="64" height="64"/>
 </tile>
</tileset>
