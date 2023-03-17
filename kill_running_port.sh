kill -9 $(lsof -i | grep 18080 | awk '{print $2}')
kill -9 $(lsof -i | grep 8793 | awk '{print $2}')
