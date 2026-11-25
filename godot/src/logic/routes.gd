class_name Routes
extends RefCounted
## Route constants and $TOKEN resolution (port of logic/Routes.java).

const ARLAND := "arland"
const SOFIA := "sofia"


static func valid(r) -> bool:
	return r == ARLAND or r == SOFIA


static func partner(r: String) -> String:
	return SOFIA if r == ARLAND else ARLAND


static func room(r: String) -> String:
	return r + "_room"


static func display(r: String) -> String:
	return "Arland" if r == ARLAND else "Sofia"


## Replace $ROOM, $PARTNER, $RU and $ROUTE in data strings.
static func resolve(s, r: String):
	if not (s is String) or s.find("$") < 0:
		return s
	return s.replace("$ROOM", room(r)).replace("$PARTNER", partner(r)).replace("$RU", r.to_upper()).replace("$ROUTE", r)
