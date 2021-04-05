SCRIPT_PATH=$(dirname "$0")
ITEM_COLOUR=$(tput setaf 0 && tput setab 4)
NOTICE_COLOUR=$(tput setaf 0 && tput setab 2)
ERROR_COLOUR=$(tput setaf 0 && tput setab 1)
RESET=$(tput sgr0)

AWS_PROFILE="polybotuser"
AWS_ENDPOINT="http://localhost:8000"

colour_line() {
	echo "${1}${2}${RESET}"
}

print_item() {
	colour_line "$ITEM_COLOUR" "$1"
}

print_notice() {
	colour_line "$NOTICE_COLOUR" "$1"
}

print_error() {
	colour_line "$ERROR_COLOUR" "$1"
}

error_or_deleting_table() {
	if [ "$1" = "deleting table" ]; then
		print_notice "$1...No table to delete."
	else
		print_error "Error running this command."
	fi
}

run() {
	print_item "$1:"
	eval "$2"
	ERROR_CODE=$?
	if [ $ERROR_CODE -gt 0 ]; then
		error_or_deleting_table "$1"
	else
		print_notice "$1...success."
	fi
}

CMD_DELETE_TABLE="aws dynamodb delete-table \
	--table-name WP_Beacons \
	--profile $AWS_PROFILE \
	--endpoint-url $AWS_ENDPOINT \
	--output json \
	--query 'TableDescription.{Table:TableName, Status:TableStatus}'"
run "deleting table" "$CMD_DELETE_TABLE"

CMD_CREATE_TABLE="aws dynamodb create-table \
	--cli-input-json "file://$SCRIPT_PATH/create.json" \
	--profile $AWS_PROFILE \
	--endpoint-url $AWS_ENDPOINT \
	--output json \
	--query 'TableDescription.{Table:TableName, Status:TableStatus}'"
run "creating table" "$CMD_CREATE_TABLE"

CMD_ADD_DATA="aws dynamodb put-item \
	--cli-input-json "file://$SCRIPT_PATH/put.json" \
	--profile $AWS_PROFILE \
	--endpoint-url $AWS_ENDPOINT \
	--output json"
run "adding dummy data" "$CMD_ADD_DATA"

CMD_QUERY_ALL_AVAILABLE="aws dynamodb query \
	--table-name WP_Beacons \
	--index-name AllAvailableBeacons \
	--key-condition-expression 'TypeName = :typename AND EndTime > :timeleft' \
	--expression-attribute-values \
	'{\":typename\":{\"S\":\"Beacon\"},\":timeleft\":{\"N\":\"5\"}}' \
	--profile $AWS_PROFILE \
	--endpoint-url $AWS_ENDPOINT \
	--output json \
	--query 'Items[*].{UniqueId:UniqueId}'"
run "querying all beacons" "$CMD_QUERY_ALL_AVAILABLE"

CMD_QUERY_BY_USER_ID="aws dynamodb query \
	--table-name WP_Beacons \
	--index-name BeaconsByUserId \
	--key-condition-expression 'UserId = :userId AND EndTime > :timeleft' \
	--expression-attribute-values \
	'{\":userId\":{\"S\":\"123456789\"},\":timeleft\":{\"N\":\"5\"}}' \
	--profile $AWS_PROFILE \
	--endpoint-url $AWS_ENDPOINT \
	--output json \
	--query 'Items[*].{UniqueId:UniqueId}'"
run "querying beacons by userId" "$CMD_QUERY_BY_USER_ID"

print_notice "...done."
