#!/bin/sh

# Loading all variables from .env
export $(grep -v '^#' .env | xargs)

# TODO: Implement This
