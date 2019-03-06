#!/bin/bash

print_update_env_cmds() {
    local SRC_DIR=$1
    local DEST_DIR=$2
    local FILE_ABS_PATH=$3
    local FILE_REL_PATH="${FILE_ABS_PATH/$SRC_DIR/}"
    local TARGET_SUFFIX=$4
    local BACKUP_SUFFIX=$5
    
    FILE_REL_PATH=`echo "$FILE_REL_PATH" | sed "s/$TARGET_SUFFIX$//g"`

    local BACKUP_CMD="cp -p '$DEST_DIR$FILE_REL_PATH' '$SRC_DIR$FILE_REL_PATH$BACKUP_SUFFIX'"
    local UPDATE_CMD="cp -p '$SRC_DIR$FILE_REL_PATH$TARGET_SUFFIX' '$DEST_DIR$FILE_REL_PATH'"

    echo
    echo -e "\e[1;4m$FILE_REL_PATH\e[0m"
    echo -e "\e[96m$BACKUP_CMD\e[39m"
    echo -e "\e[93m$UPDATE_CMD\e[39m"
}

SRC_DIR=$1
DEST_DIR=$2
TARGET_SUFFIX=$3

if [[ ! -d $SRC_DIR ]]; then
    echo 'Invalid src dir.'
    exit 1
fi
if [[ ! $SRC_DIR == */ ]]; then
    SRC_DIR="$SRC_DIR/"
fi

if [[ -z $DEST_DIR ]]; then
    DEST_DIR='/var/www/html/'
else
    if [[ ! -d $DEST_DIR ]]; then
        echo 'Invalid dest dir.'
        exit 1
    fi
fi
if [[ ! $SRC_DIR == */ ]]; then
    DEST_DIR="$SRC_DIR/"
fi

if [[ -z $TARGET_SUFFIX ]]; then
    TARGET_SUFFIX='_mod'
fi

BACKUP_SUFFIX=_bk`date +%Y%m%d-%H%M`

IFS=$'\n'
for file in `find "$SRC_DIR" -regex ".*\.php$TARGET_SUFFIX$\|.*\.html$TARGET_SUFFIX$"`; do
    print_update_env_cmds "$SRC_DIR" "$DEST_DIR" "$file" "$TARGET_SUFFIX" "$BACKUP_SUFFIX"
done
echo
unset $IFS
