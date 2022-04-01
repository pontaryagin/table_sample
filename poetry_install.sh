#!/bin/bash -e

hash="$(cat poetry.lock | sha1sum | sha1sum | cut -f1 -d' ')"
venv_dir=$HOME/.cache/poetry-install/$hash
activate=$venv_dir/bin/activate
lock_file=$venv_dir.lock

exec 200>$lock_file
read_lock(){ flock -s 200; }
write_lock(){ flock -x 200; }

if [[ -e $venv_dir ]]; then
    echo "venv $venv_dir already exists"
    read_lock
    cp -T -r $venv_dir .venv
    exit
fi
poetry config --local virtualenvs.in-project true
poetry install
echo "lock " $lock_file
write_lock
if [[ ! -e $venv_dir ]]; then
    cp -T -r .venv $venv_dir
fi

