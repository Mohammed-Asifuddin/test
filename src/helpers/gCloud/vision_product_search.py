from google.cloud import vision


def get_similar_products_file(
    project_id, location, product_set_id, product_category, image_uri
):
    """Search similar products to image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_category: Category of the product.
        image_uri: Image URL link / GCS storage gsutil link.
        filter: Condition to be applied on the labels.
                Example for filter: (color = red OR color = blue) AND style = kids
                It will search on all products with the following labels:
                color:red AND style:kids
                color:blue AND style:kids
        max_results: The maximum number of results (matches) to return. If omitted, all results are returned.
    """

    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()

    # image_bytes = base64.b64decode(image_uri)
    # print(type(image_bytes))
    image = vision.Image(content=image_uri)

    # product search specific parameters
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location, product_set=product_set_id
    )
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path, product_categories=[product_category]
    )
    image_context = vision.ImageContext(product_search_params=product_search_params)

    # Search products similar to the image.
    response = image_annotator_client.product_search(image, image_context=image_context)

    # index_time = response.product_search_results.index_time
    results = response.product_search_results.results
    # product_id_list = []
    # for result in results:
    #     product = result.product
    #     split_image = result.image.split('/')
    #     product_id_list.append(split_image[-1])
    return results[0].product.product_labels[0].value


def import_product_sets(project_id, location, gcs_uri):
    """Import images of different products in the product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        gcs_uri: Google Cloud Storage URI.
            Target files must be in Product Search CSV format.
    """
    client = vision.ProductSearchClient()
    location_path = f"projects/{project_id}/locations/{location}"
    gcs_source = vision.ImportProductSetsGcsSource(csv_file_uri=gcs_uri)
    input_config = vision.ImportProductSetsInputConfig(gcs_source=gcs_source)
    response = client.import_product_sets(
        parent=location_path, input_config=input_config
    )
    print(response)
    print("Processing operation name: {}".format(response.operation.name))
    result = response.result()
    print("Processing done.")
    for i, status in enumerate(result.statuses):
        print("Status of processing line {} of the csv: {}".format(i, status))
        if status.code == 0:
            reference_image = result.reference_images[i]
            print(reference_image)
        else:
            print("Status code not OK: {}".format(status.message))
