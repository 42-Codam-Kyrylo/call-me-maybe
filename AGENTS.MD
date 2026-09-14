# Agent Coding Guidelines and Rules

This document outlines the coding standards, conventions, and rules to follow for this project to maintain code quality, readability, and consistency.

## 1. Dependency Versions and Compatibility
* **Use Modern Libraries**: Always use the features of the latest version of the libraries installed (e.g., Pydantic v2).
* **No Unnecessary Backwards Compatibility**: Do not write backward compatibility layers (e.g., for Pydantic v1) if it makes the code harder to read, maintain, and understand.

## 2. DRY (Don't Repeat Yourself)
* **Helper Functions**: Whenever multiple functions share almost the same logic (like file reading, JSON parsing, or validation), abstract the shared logic into a generic helper function to avoid code duplication. 

## 3. Python Imports
* **Top of the File**: Always put imports at the top of the file for clarity and to follow PEP 8 standard. Avoid dynamic imports inside functions or methods unless absolutely necessary (e.g., for breaking circular dependencies).

## 4. Python Packages and Modules
* **`__init__.py`**: Always include an `__init__.py` file in package directories. While Python 3.3+ supports implicit namespace packages, explicitly marking directories as packages is best practice for tooling, linters, and explicit structure.
* **Clean Public APIs**: Export commonly used functions and classes from the package's `__init__.py` using `__all__`. This allows other modules to import from the package directly (e.g., `from package import function` instead of `from package.module import function`), keeping import paths clean and concise.
