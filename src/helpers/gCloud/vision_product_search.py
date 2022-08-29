from google.cloud import vision


def get_similar_products_file(
    project_id, location, product_set_id, product_categories, image_uri
):
    """
    Search similar products to image.
    """

    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_uri)
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location, product_set=product_set_id
    )
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path, product_categories=product_categories
    )
    image_context = vision.ImageContext(product_search_params=product_search_params)
    response = image_annotator_client.product_search(image, image_context=image_context)
    results = response.product_search_results.results
    return results[0]


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
