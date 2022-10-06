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
    image_context = vision.ImageContext(
        product_search_params=product_search_params)
    response = image_annotator_client.product_search(
        image, image_context=image_context)
    results = response.product_search_results.results
    if len(results) >= 1:
        return results[0]
    return response


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
    print("Processing done.")


def delete_product(project_id, location, product_id):
    """Delete the product and all its reference images.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # Delete a product.
    client.delete_product(name=product_path)
    print('Product deleted.')


def delete_product_set(project_id, location, product_set_id):
    """Delete a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product set.
    product_set_path = client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)

    # Delete the product set.
    client.delete_product_set(name=product_set_path)
    print('Product set deleted.')
