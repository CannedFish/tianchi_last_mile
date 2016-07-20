  Show all information in a plot in which sites, spots and shops are points and orders are lines between.

## Target
  Use the least time to delivery the most packages.

## Idea 1
  Thinking each site as a center of a cluster which spots are naturally belongs to. Then split shops into the cluster it should be.

## Idea 2
  Find spots near shops and route based on the pickup time of shops.

## Idea 3
  All spots are split by the relation between them and sites which can be seen as zones. Relations between shops and spots are links of zones. Each o2o order will transfer a courier from a zone to the other.
  
  1. Use zone to mark spots
  2. Use kNN to classify shops
  3. Calculate total eb_orders of one zone to initialize the number of orders
  4. Find the zone which a shop of a o2o_order belongs to and add to initial order number
  5. Find the zone which a spot of a o2o_order belongs to
  6. Arrange couriers based on initial order number
  7. Sort spots of each site based on the number of package of an order(Greedy algorithm)
  8. Adjust the number of couriers of each zone based on the time when they finish their jobs.

# Work flow
  1. Initialize zones
  2. Initialize courierpool of each zone
  3. Execute plans of zones
  4. Gather couriers' work path

# Algorithm ----- DP
  1. Target: d(i), i<=140(The least time use to send 140 packages at most)
  2. State function: d(i) = min(d(i-vj) + d(vj)) (vj defines number of package of the jth order)
