class Messages:

    START_MSG = (
        "Hi there {}.\n\nI'm a YouTube Uploader Bot. You can use me to upload any Telegram video to YouTube "
        "once you authorize me. You can know more from /help.\n\nThank you."
    )

    HELP_MSG = [
        ".",
        "Hi there.\n\nFirst things first. You should know that YouTube processes every uploaded video. "
        "Its AI can detect copyrighted content quickly and may block publishing.\n\n"
        "Read all pages to understand how I work.",

        "**Let’s learn how I work.**\n\n"
        "**Step 1:** Authorize me to upload to your YouTube channel.\n\n"
        "**Step 2:** Forward any Telegram video to me.\n\n"
        "**Step 3:** Reply `/upload` to the video. You can optionally add a title.\n\n"
        "**Step 4:** I download and upload it.\n\n"
        "**Step 5:** I send you the YouTube link.",

        "**Create your YouTube channel**\n\n"
        "1. Sign in to YouTube\n"
        "2. Try uploading or commenting\n"
        "3. Create channel if prompted\n"
        "4. Confirm details",

        "**Verify your YouTube account**\n\n"
        "Verification allows uploads longer than 15 minutes.\n"
        "[Verify here](http://www.youtube.com/verify)\n\n"
        "Unverified accounts may have restricted uploads.",

        "**Now let's authorize.**\n\n"
        "Open the provided link, allow access, copy the code, and send:\n"
        "/authorise YOUR_CODE\n\n"
        "Don’t worry — your data is safe."
    ]

    NOT_A_REPLY_MSG = "Please reply to a video file."

    NOT_A_MEDIA_MSG = "No media file found. " + NOT_A_REPLY_MSG

    NOT_A_VALID_MEDIA_MSG = "This is not a valid media."

    # ✅ FIXED (multi-line string)
    DAILY_QOUTA_REACHED = (
        "Looks like you are trying to upload more than 6 videos today!\n"
        "YouTube usually allows around 6 uploads per day, so this may fail."
    )

    PROCESSING = "Processing..."

    NOT_AUTHENTICATED_MSG = (
        "You have not authorized me yet.\nUse /help to authenticate."
    )

    NO_AUTH_CODE_MSG = "No code provided. Please send the authorization code."

    AUTH_SUCCESS_MSG = (
        "✅ Successfully authenticated!\nNow you can upload videos."
    )

    AUTH_FAILED_MSG = "❌ Authentication failed.\nDetails: {}"

    AUTH_DATA_SAVE_SUCCESS = "✅ Authorization data saved successfully!"
