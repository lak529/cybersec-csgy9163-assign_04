#!/bin/bash
app="spell_check"
openssl rand -base64 20 | docker secret create spell_check_secret_key -
printf "Administrator@1" | docker secret create spell_check_admin_pw -
printf "12345678901" | docker secret create spell_check_admin_mfa -