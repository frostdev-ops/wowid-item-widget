# wowid-item-widget
## Overview

The `wowid-item-widget` is a graphical user interface (GUI) application designed to modify item properties in a remote JSON5 configuration file. It connects to a remote server via SFTP, allowing users to read, update, and save item attributes seamlessly.

## Features

- **Remote File Access**: Connect to a remote server using SFTP to read and write JSON5 configuration files.
- **Item Modification**: Easily update item attributes and modifiers.
- **User-Friendly Interface**: Intuitive GUI built with Tkinter for easy navigation and operation.
- **Customization**: Update appearance settings including background color, font size, and more.
- **Settings Management**: Update SFTP credentials and file paths directly from the application.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/wowid-item-widget.git
    ```
2. Navigate to the project directory:
    ```sh
    cd wowid-item-widget
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```
2. Follow the prompts to enter your SFTP credentials and remote file path.
3. Use the GUI to navigate and modify item properties.

## Building Executable

To build a standalone executable, use PyInstaller:
```sh
python pyinstaller.py
```

This will generate a single executable file with the specified icon and name.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI components.
- [Paramiko](https://www.paramiko.org/) for SFTP support.
- [JSON5](https://json5.org/) for handling JSON5 files.
