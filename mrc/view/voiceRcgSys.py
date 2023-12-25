import speech_recognition as sr


class VoiceRcg:
    def __init__(self):
        self.__recognizer = sr.Recognizer()
        self.__isRecording = False
        self.__onResult = None

    def registerResultEventListener(self, callback):
        self.__onResult = callback

    def isRecording(self):
        return self.__isRecording

    def record(self):
        self.__isRecording = True

        result = None

        with sr.Microphone() as source:
            print("Say something...")
            self.__recognizer.adjust_for_ambient_noise(
                source
            )  # Adjust for ambient noise

            try:
                # Listen for speech using the microphone
                audio = self.__recognizer.listen(source, timeout=3)

                # Use the Google Web Speech API to recognize the audio
                result = self.__recognizer.recognize_google(audio)
                print("You said:", result)
            except sr.WaitTimeoutError:
                print("Input waiting time exceeded. ")
            except sr.UnknownValueError:
                print("Sorry, could not understand audio.")
            except sr.RequestError as e:
                print(f"Error with the API request;")

        self.__isRecording = False
        if self.__onResult != None:
            self.__onResult(result)
