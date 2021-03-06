POST_SCHEMA = {
  "create": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "minLength": 2,
        "maxLength": 100
      },
      "body": {
        "type": "string"
      },
      "is_active": {
        "type": "boolean"
      },
      "status": {
        "type": "string",
        "enum": [
          "active",
          "passive",
          "draft"
        ]
      }
    },
    "required": [
      "title",
      "body",
      "is_active",
      "status"
    ],
    "additionalProperties": False
  },
  "update": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "minLength": 2,
        "maxLength": 100
      },
      "body": {
        "type": "string"
      },
      "is_active": {
        "type": "boolean"
      },
      "status": {
        "type": "string",
        "enum": [
          "active",
          "passive",
          "draft"
        ]
      }
    },
    "additionalProperties": False
  },
  "query": {
    "type": "object",
    "properties": {
      "where": {
        "type": "object"
      },
      "select": {
        "type": "object"
      }
    },
    "additionalProperties": False
  }
}