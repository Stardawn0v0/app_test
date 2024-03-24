#!/bin/sh
for package in $(pm list packages | cut -d':' -f2)
do
    apk_path=$(pm path $package 2>/dev/null | cut -d':' -f2)
    if [ -z "$apk_path" ]; then
        continue
    fi
    app_name_line=$(/data/local/tmp/aapt-arm-pie dump badging "$apk_path" 2>/dev/null | grep "application-label:")

    if [ ! -z "$app_name_line" ]; then
        app_name=$(echo $app_name_line | cut -d"'" -f2)

        # 判断应用类型（用户应用或系统应用）并输出信息
        if echo $apk_path | grep -q '/system/'; then
            echo "system<trim>$app_name<trim>$package"
        else
            echo "user<trim>$app_name<trim>$package"
        fi
    fi
done