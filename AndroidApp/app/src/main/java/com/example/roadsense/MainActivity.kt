
package com.example.roadsense

import android.os.Bundle
import android.graphics.Color
import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Environment
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import java.io.BufferedWriter
import java.io.File
import java.io.FileWriter
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : AppCompatActivity(), SensorEventListener {

    private var isMonitoring = false

    private lateinit var sensorManager: SensorManager

    private var accelerometer: Sensor? = null
    private var linearAcceleration: Sensor? = null

    private lateinit var startButton: Button
    private lateinit var statusText: TextView
    private lateinit var accelerationText: TextView

    private var csvWriter: BufferedWriter? = null
    private var csvFile: File? = null

    private var sampleCount = 0
    private var rawReadings = "Waiting..."
    private var linearReadings = "Waiting..."

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        ViewCompat.setOnApplyWindowInsetsListener(
            findViewById(R.id.main)
        ) { v, insets ->
            val systemBars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars()
            )

            v.setPadding(
                systemBars.left,
                systemBars.top,
                systemBars.right,
                systemBars.bottom
            )

            insets
        }

        startButton = findViewById(R.id.btnStartMonitoring)
        statusText = findViewById(R.id.txtMonitoringStatus)
        accelerationText = findViewById(R.id.txtAcceleration)

        sensorManager =
            getSystemService(Context.SENSOR_SERVICE) as SensorManager

        accelerometer =
            sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

        linearAcceleration =
            sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)

        startButton.setOnClickListener {
            if (!isMonitoring) {
                startMonitoring()
            } else {
                stopMonitoring()
            }
        }

        showReadings()
    }

    private fun startMonitoring() {

        val rawSensor = accelerometer

        if (rawSensor == null) {
            Toast.makeText(
                this,
                "Accelerometer not available",
                Toast.LENGTH_LONG
            ).show()
            return
        }

        try {
            val directory =
                getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS)
                    ?: filesDir

            if (!directory.exists()) {
                directory.mkdirs()
            }

            val timestamp = SimpleDateFormat(
                "yyyyMMdd_HHmmss",
                Locale.US
            ).format(Date())

            csvFile = File(
                directory,
                "RoadSense_$timestamp.csv"
            )

            csvWriter = BufferedWriter(FileWriter(csvFile!!))

            csvWriter?.write("timestamp_ns,sensor_type,x,y,z")
            csvWriter?.newLine()
            csvWriter?.flush()

        } catch (e: IOException) {
            closeCsvWriter()

            Toast.makeText(
                this,
                "Could not create CSV file",
                Toast.LENGTH_LONG
            ).show()
            return
        }

        sampleCount = 0
        rawReadings = "Waiting..."
        linearReadings = "Waiting..."

        isMonitoring = true

        val rawRegistered = sensorManager.registerListener(
            this,
            rawSensor,
            SensorManager.SENSOR_DELAY_GAME
        )

        if (!rawRegistered) {
            isMonitoring = false
            closeCsvWriter()

            Toast.makeText(
                this,
                "Could not start accelerometer",
                Toast.LENGTH_LONG
            ).show()
            return
        }

        val linearRegistered = linearAcceleration?.let {
            sensorManager.registerListener(
                this,
                it,
                SensorManager.SENSOR_DELAY_GAME
            )
        } ?: false

        statusText.text = "Monitoring Active"
        statusText.setTextColor(Color.parseColor("#22C55E"))
        startButton.text = "STOP MONITORING"

        val message = if (linearRegistered) {
            "Raw + Linear acceleration active"
        } else {
            "Raw active; linear sensor unavailable"
        }

        Toast.makeText(
            this,
            message,
            Toast.LENGTH_LONG
        ).show()

        showReadings()
    }

    override fun onSensorChanged(event: SensorEvent?) {

        if (!isMonitoring || event == null) return

        val x = event.values[0]
        val y = event.values[1]
        val z = event.values[2]

        val sensorName = when (event.sensor.type) {

            Sensor.TYPE_ACCELEROMETER -> {
                rawReadings = String.format(
                    Locale.US,
                    "X: %.3f  Y: %.3f  Z: %.3f",
                    x, y, z
                )
                "raw_accelerometer"
            }

            Sensor.TYPE_LINEAR_ACCELERATION -> {
                linearReadings = String.format(
                    Locale.US,
                    "X: %.3f  Y: %.3f  Z: %.3f",
                    x, y, z
                )
                "linear_acceleration"
            }

            else -> return
        }

        showReadings()

        val csvRow = String.format(
            Locale.US,
            "%d,%s,%.6f,%.6f,%.6f",
            event.timestamp,
            sensorName,
            x, y, z
        )

        try {
            csvWriter?.write(csvRow)
            csvWriter?.newLine()

            sampleCount++

            if (sampleCount % 20 == 0) {
                csvWriter?.flush()
            }

        } catch (e: IOException) {
            stopMonitoring()

            Toast.makeText(
                this,
                "Recording stopped due to a file error",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    private fun showReadings() {
        accelerationText.text =
            "RAW ACCELERATION\n$rawReadings\n\n" +
                    "LINEAR ACCELERATION\n$linearReadings"
    }

    private fun closeCsvWriter() {
        try {
            csvWriter?.flush()
            csvWriter?.close()
        } catch (e: IOException) {
            // File closing error handled separately
        }

        csvWriter = null
    }

    private fun stopMonitoring() {

        if (!isMonitoring) return

        sensorManager.unregisterListener(this)

        closeCsvWriter()

        isMonitoring = false

        statusText.text = "Not Monitoring"
        statusText.setTextColor(Color.parseColor("#FBBF24"))
        startButton.text = "START MONITORING"

        accelerationText.text =
            "Recording stopped\nSensor events saved: $sampleCount"

        Toast.makeText(
            this,
            "CSV saved: ${csvFile?.name}",
            Toast.LENGTH_LONG
        ).show()
    }

    override fun onAccuracyChanged(
        sensor: Sensor?,
        accuracy: Int
    ) {
        // No action needed for now
    }

    override fun onPause() {
        super.onPause()

        if (isMonitoring) {
            stopMonitoring()
        }
    }
}
