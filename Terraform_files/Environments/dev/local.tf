locals {

  uniq_doc = ["prod1", "prod2", "prod3", "prod4", "prod5"]
  index    = ["0", "1", "2", "3", "4"]

  #prod_fields=[field1,field2,field3,field4,field5]
  #Firestore Fields For Configuration Collection
  conf_field = jsonencode(
    {
      "pubsub_video_to_image_topic_name" = {
        stringValue = "btl_video_to_image"
      },
      "secret_manager_key_for_user_flow" = {
        stringValue = "user_flow_api_auth"
      }
    }
  )
  #Firestore Values for product Document
  category      = ["Packaged goods", "Toys", "Home goods", "Apparel", "General"]
  category_code = ["packagedgoods-v1", "toys-v2", "homegoods-v2", "apparel-v2", "general-v1"]
  category_id   = ["9yss1MQM6He4B9jegID2", "LRsrZ0z3tnCaoDR3MjZm", "RRH2RXXJBvB2NvFBML22", "b0GrC72kmBpEJfGtmCKl", "xeUnjYuDvlMgRvsaPNPF"]
  description = [
    "Packaged goods are any products that are shown through a wrapper, container, box, etc.",
    "Toys are any games or playthings intended for consumer use.",
    "Home goods are products you find around the house: appliances, furniture, furnishings, etc.",
    "Apparel products are clothing items: bags, shoes, garments, etc.",
    "This classification allows you a more generalized category option for products. Vision API Product Search then detects and maps the appropriate product category to the product for you."

  ]




}