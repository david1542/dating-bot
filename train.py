import os
import argparse
import pandas as pd
from tensorflow import keras
from datetime import datetime
from clearml import Task

from src.utils.data import create_dataset, load_metadata, split_metadata


def create_dataframe(X, y):
    return pd.DataFrame({'file_path': X, 'label': y})

def create_model(dropout_rate=0.1):
    backbone = keras.applications.Xception(
        weights='imagenet',  # Load weights pre-trained on ImageNet.
        input_shape=(256, 256, 3),
        include_top=False)

    backbone.trainable = False
    inputs = keras.Input(shape=(256, 256, 3))

    # We make sure that the base_model is running in inference mode here,
    # by passing `training=False`
    x = backbone(inputs, training=False)

    # Convert features of shape `base_model.output_shape[1:]` to vectors
    x = keras.layers.GlobalAveragePooling2D()(x)

    # A Dense classifier with a single unit (binary classification)
    x = keras.layers.Dense(256, activation='relu')(x)
    x = keras.layers.Dropout(rate=dropout_rate)(x)
    x = keras.layers.Dense(128, activation='relu')(x)
    x = keras.layers.Dropout(rate=dropout_rate)(x)
    outputs = keras.layers.Dense(1, activation='sigmoid')(x)
    model = keras.Model(inputs, outputs)
    
    return model


def train(task_name: str, args: argparse.Namespace):
    # Create task path
    task_path = os.path.join(args.base_path, task_name)
    os.mkdir(task_path)

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
    loss = keras.losses.BinaryCrossentropy(from_logits=False)
    metrics = [
        keras.metrics.BinaryAccuracy(threshold=0.5)
    ]

    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    best_model_path = os.path.join(task_path, 'saved_models', 'best', 'model.h5')
    model_logs_path = os.path.join(task_path, 'logs')
    callbacks = [
        keras.callbacks.ModelCheckpoint(filepath=best_model_path, save_best_only=True, monitor='val_loss', mode='min', verbose=1),
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, min_delta=0.00001),
        keras.callbacks.TensorBoard(log_dir=model_logs_path, write_images=False)
    ]
    
    # Train the model
    model.fit(ds_train, validation_data=ds_valid, validation_freq=5,
        epochs=args.epochs, callbacks=callbacks)

    # Load best checkpoint & evaluate the model
    model = keras.models.load_model(best_model_path, compile=False)
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
    parser.add_argument("--use-clearml", action="store_true")
    parser.add_argument('--epochs', type=int, default=100)

    args = parser.parse_args()

    # Define params
    project_name = 'dating-bot'
    start_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    task_name = f'{project_name}_{start_time}'

    # Init ClearML task
    if args.use_clearml:
        Task.init(project_name=project_name, task_name=task_name)
    
    train(task_name, args)