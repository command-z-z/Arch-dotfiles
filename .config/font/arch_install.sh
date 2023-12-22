array=(HackNerdFont JetBrainsMono OperatorMono)
current_dir=`pwd`
for font in ${array[@]}
do
    sudo cp -r ${font} /usr/share/fonts/
    cd /usr/share/fonts/${font}
	sudo fc-cache -fv 
    cd ${current_dir}
done

