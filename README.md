  Show all information in a plot in which sites, spots and shops are points and orders are lines between.

## Target
  Use the least time to delivery the most packages.

## Idea 1
  Thinking each site as a center of a cluster which spots are naturally belongs to. Then split shops into the cluster it should be.

## Idea 2
  Find spots near shops and route based on the pickup time of shops.

## Idea 3
  All spots are splited by the relation between them and sites which can be seen as zones. Relations between shops and spots are links of zones. Each o2o order will transfor a courier from a zone to the other.
  
  1. Use zone to mark spots
  2. Use kNN to classify shops
