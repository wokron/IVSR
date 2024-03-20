json_data = """
{
    "file_name": "balabala-android.apk",
    "app_name": "Balabala",
    "size": "250TB",
    "package_name": "balabala",
    "main_activity": "balabala.MainActivity",
    "icon_path": "/some/path",
    "exported_activities": "['balabala.XActivity']",
    "activities": [
        "balabala.MainActivity"
    ],
    "receivers": [
        "balabala.XReceiver"
    ],
    "providers": [
        "balabala.service.XProvider"
    ],
    "services": [
        "balabala.Xervice"
    ],
    "permissions": {
        "android.permission.RECEIVE_BOOT_COMPLETED": {
            "status": "normal",
            "info": "automatically start at boot",
            "description": "Allows an application to start itself as soon as the system has finished booting. This can make it take longer to start the phone and allow the application to slow down the overall phone by always running."
        }
    },
    "malware_permissions": {
        "top_malware_permissions": [
            "android.permission.INTERNET"
        ],
        "other_abused_permissions": [
            "android.permission.CHANGE_NETWORK_STATE"
        ],
        "total_malware_permissions": 1,
        "total_other_permissions": 2
    },
    "certificate_analysis": {
        "certificate_info": "balabalabala",
        "certificate_findings": [
            [
                "info",
                "Application is signed with a code signing certificate",
                "Signed Application"
            ]
        ]
    },
    "manifest_analysis": {
        "manifest_findings": [
            {
                "rule": "vulnerable_os_version",
                "title": "App can be installed on a vulnerable upatched Android version<br>Android 5.0-5.0.2, [minSdk=21]",
                "severity": "high",
                "description": "This application can be installed on an older version of android that has multiple unfixed vulnerabilities. These devices won't receive reasonable security updates from Google. Support an Android version => 10, API 29 to receive reasonable security updates.",
                "name": "App can be installed on a vulnerable upatched Android version 5.0-5.0.2, [minSdk=21]",
                "component": [
                    "4",
                    "1"
                ]
            }
        ]
    },
    "network_security": {
        "network_findings": [
            {
                "scope": [
                    "*"
                ],
                "description": "Base config is configured to trust system certificates.",
                "severity": "warning"
            }
        ],
        "network_summary": {
            "high": 1,
            "warning": 1,
            "info": 0,
            "secure": 0
        }
    },
    "binary_analysis": [
        {
            "name": "apktool_out/lib/armeabi-v7a/libbridge.so",
            "nx": {
                "is_nx": true,
                "severity": "info",
                "description": "The binary has NX bit set. This marks a memory page non-executable making attacker injected shellcode non-executable."
            },
            "stack_canary": {
                "has_canary": true,
                "severity": "info",
                "description": "This binary has a stack canary value added to the stack so that it will be overwritten by a stack buffer that overflows the return address. This allows detection of overflows by verifying the integrity of the canary before function return."
            },
            "relocation_readonly": {
                "relro": "Full RELRO",
                "severity": "info",
                "description": "This shared object has full RELRO enabled. RELRO ensures that the GOT cannot be overwritten in vulnerable ELF binaries. In Full RELRO, the entire GOT (.got and .got.plt both) is marked as read-only."
            },
            "rpath": {
                "rpath": null,
                "severity": "info",
                "description": "The binary does not have run-time search path or RPATH set."
            },
            "runpath": {
                "runpath": null,
                "severity": "info",
                "description": "The binary does not have RUNPATH set."
            },
            "fortify": {
                "is_fortified": false,
                "severity": "warning",
                "description": "The binary does not have any fortified functions. Fortified functions provides buffer overflow checks against glibc's commons insecure functions like strcpy, gets etc. Use the compiler option -D_FORTIFY_SOURCE=2 to fortify functions. This check is not applicable for Dart/Flutter libraries."
            },
            "symbol": {
                "is_stripped": false,
                "severity": "warning",
                "description": "Symbols are available."
            }
        }
    ],
    "android_api": {
        "api_notifications": {
            "files": {
                "balabala/module/dfsfsd.java": "8,30"
            },
            "metadata": {
                "description": "Android Notifications",
                "severity": "info"
            }
        }
    },
    "code_analysis": {
        "findings": {
            "android_hardcoded": {
                "files": {
                    "balabala/service/dfdf.java": "386,239"
                },
                "metadata": {
                    "cvss": 7.4,
                    "cwe": "CWE-312: Cleartext Storage of Sensitive Information",
                    "masvs": "MSTG-STORAGE-14",
                    "owasp-mobile": "M9: Reverse Engineering",
                    "ref": "https://github.com/MobSF/owasp-mstg/blob/master/Document/0x05d-Testing-Data-Storage.md#checking-memory-for-sensitive-data-mstg-storage-10",
                    "description": "Files may contain hardcoded sensitive information like usernames, passwords, keys etc.",
                    "severity": "warning"
                }
            }
        }
    },
    "permission_mapping": {
        "android.permission.QUERY_ALL_PACKAGES": {
            "123.java": "7,211",
            "com/dafewraer$queryProfileProviders$2.java": "6,5667"
        }
    },
    "domains": {
        "github.com": {
            "bad": "no",
            "geolocation": {
                "ip": "20.205.243.166",
                "country_short": "US",
                "country_long": "United States of America",
                "region": "Washington",
                "city": "Redmond",
                "latitude": "47.682899",
                "longitude": "-122.120903"
            },
            "ofac": false
        }
    },
    "secrets": [
        "this_is_not_secrets"
    ]
}
"""
