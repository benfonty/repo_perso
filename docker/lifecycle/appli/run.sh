[[ $# -ne 1 ]] && echo usage run.sh [nb serveurs] && exit -1

num=1
while [ $num -le $((0 + $1)) ]
do
   docker run --volumes-from data --volumes-from logs -d -p $((5000 + $num)):5000 bfonty/appli
   num=$(($num + 1))
done
