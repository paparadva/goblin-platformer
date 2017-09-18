<?xml version="1.0" encoding="UTF-8"?>
<tileset name="blocks" tilewidth="32" tileheight="32" tilecount="4" columns="4">
 <image source="blocks.png" trans="00ff00" width="128" height="32"/>
 <tile id="0">
  <properties>
   <property name="type" value="hardblock"/>
  </properties>
 </tile>
 <tile id="1">
  <properties>
   <property name="hits" type="int" value="1"/>
   <property name="type" value="breakable"/>
  </properties>
 </tile>
 <tile id="2">
  <properties>
   <property name="coins" type="bool" value="true"/>
   <property name="hits" type="int" value="6"/>
   <property name="type" value="with_coins"/>
  </properties>
 </tile>
 <tile id="3">
  <properties>
   <property name="type" value="exhausted"/>
  </properties>
 </tile>
</tileset>
