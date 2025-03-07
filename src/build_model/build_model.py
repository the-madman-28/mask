from spacy.cli.train import train

def train_spacy_model(config_file_path: str, output_file_path:str) -> None:
    '''Build Spacy model.
    
    :params config_file_path: Spacy config file path
    :params output_file_path: Model output path'''
    train(config_path=config_file_path, output_path=output_file_path)

if __name__ == "__main__":
    model_extension = input('Input input model extension: ')
    train_spacy_model(config_file_path="./config.cfg", output_file_path=f"./model/spacy_{model_extension}")