import os
import argparse
import pandas as pd
from tensorflow import keras
from datetime import datetime

from src.utils.data import create_dataset, load_metadata, split_metadata


def create_dataframe(X, y):
    return pd.DataFrame({'file_path': X, 'label': y})

def create_model():
    backbone = keras.applications.Xception(
        weights='imagenet',  # Load weights pre-trained on ImageNet.
        input_shape=(256, 256, 3),
        include_top=False)

    inputs = keras.Input(shape=(256, 256, 3))

    # We make sure that the base_model is running in inference mode here,
    # by passing `training=False`. This is important for fine-tuning, as you will
    # learn in a few paragraphs.
    x = backbone(inputs, training=False)

    # Convert features of shape `base_model.output_shape[1:]` to vectors
    x = keras.layers.GlobalAveragePooling2D()(x)

    # A Dense classifier with a single unit (binary classification)
    outputs = keras.layers.Dense(1)(x)
    model = keras.Model(inputs, outputs)
    
    return model


def train(args: argparse.Namespace):
    # Create output dir
    start_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join(args.base_path, start_time)
    os.mkdir(output_dir)

    df = load_metadata()

    # Split the data to train and test
    train_images, valid_images, test_images = split_metadata(df, train_frac=0.7, valid_frac=0.15)

    # Create datasets
    ds_train = create_dataset(train_images)
    ds_valid = create_dataset(valid_images)
    ds_test = create_dataset(test_images)
        
    # Create the model
    model = create_model()

    # Compile the model
    optimizer = keras.optimizers.Adam()
    loss = keras.losses.BinaryCrossentropy(from_logits=True)
    metrics = [
        keras.metrics.Accuracy()
    ]

    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    callbacks = [
        keras.callbacks.ModelCheckpoint(filepath='/ho', save_best_only=True, monitor='val_loss', mode='min', verbose=1),
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, min_delta=0.00001)
    ]
    
    # Train the model
    model.fit(ds_train, validation_data=ds_valid, validation_freq=5,
        epochs=args.epochs, callbacks=callbacks)

    # Load best checkpoint & evaluate the model
    model_path = f'{output_dir}/saved_model/best/model.h5'
    model = keras.load_model(model_path, compile=False)
    model.compile(loss=loss, metrics=metrics)

    valid_performance = model.evaluate(ds_valid, return_dict=True)
    test_performance = model.evaluate(ds_test, return_dict=True)

    if args.use_clearml:
        pass
        # logger = trainer._clearml_task.get_logger()

        # # Log test loss and metrics to ClearML
        # logger.report_text(f"valid_performance: {valid_performance}")
        # logger.report_text(f"test_performance: {test_performance}")
    else:
        print(f"valid_performance: {valid_performance}")
        print(f"test_performance: {test_performance}")
    
    return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-path', type=str, required=True)
    parser.add_argument('--epochs', type=int, default=100)

    args = parser.parse_args()

    train(args)