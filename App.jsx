import React from 'react';
import { Cloud, Droplets, Thermometer, Radio, Database, BarChart3, Bell, Wifi, Sun, CloudRain } from 'lucide-react';

export default function AgricultureArchitecture() {
  return (
    <div className="w-full h-full bg-gradient-to-br from-green-50 to-blue-50 p-8 overflow-auto">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-green-800">
          🌱 Smart Agriculture Soil Monitoring System
        </h1>
        <p className="text-center text-lg text-gray-600 mb-8">
          IoT-to-Cloud Solution for Precision Irrigation
        </p>
        
        {/* Architecture Layers */}
        <div className="space-y-6">
          
          {/* Field Layer */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-600">
            <div className="flex items-center mb-4">
              <Droplets className="w-7 h-7 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-800">1. Field Layer (IoT Sensors)</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="flex items-center mb-2">
                  <Droplets className="w-5 h-5 text-green-600 mr-2" />
                  <h3 className="font-bold text-green-800">Soil Moisture</h3>
                </div>
                <p className="text-sm text-gray-700 mb-2">Capacitive sensor measures volumetric water content</p>
                <p className="text-xs text-gray-500">Range: 0-100%</p>
                <p className="text-xs text-gray-500">Depth: 10cm</p>
              </div>
              
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <div className="flex items-center mb-2">
                  <Thermometer className="w-5 h-5 text-orange-600 mr-2" />
                  <h3 className="font-bold text-orange-800">Soil Temperature</h3>
                </div>
                <p className="text-sm text-gray-700 mb-2">DS18B20 digital sensor</p>
                <p className="text-xs text-gray-500">Range: -10 to 85°C</p>
                <p className="text-xs text-gray-500">Accuracy: ±0.5°C</p>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <div className="flex items-center mb-2">
                  <Sun className="w-5 h-5 text-yellow-600 mr-2" />
                  <h3 className="font-bold text-yellow-800">Ambient Conditions</h3>
                </div>
                <p className="text-sm text-gray-700 mb-2">DHT22: Air temp & humidity</p>
                <p className="text-xs text-gray-500">Light sensor (optional)</p>
                <p className="text-xs text-gray-500">For evaporation calc</p>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center mb-2">
                  <CloudRain className="w-5 h-5 text-blue-600 mr-2" />
                  <h3 className="font-bold text-blue-800">Rainfall Detection</h3>
                </div>
                <p className="text-sm text-gray-700 mb-2">Rain sensor (optional)</p>
                <p className="text-xs text-gray-500">Skip irrigation if rain detected</p>
              </div>
            </div>
          </div>

          {/* Edge Processing Layer */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-600">
            <div className="flex items-center mb-4">
              <Radio className="w-7 h-7 text-blue-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-800">2. Edge Processing (ESP32/Arduino)</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">Data Collection</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Read sensors every 5 minutes</li>
                  <li>• Calculate rolling averages</li>
                  <li>• Detect sensor anomalies</li>
                  <li>• Battery monitoring</li>
                </ul>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">Local Decision Making</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• <strong>Rule:</strong> If moisture &lt; 30%</li>
                  <li>• <strong>Action:</strong> Trigger irrigation alert</li>
                  <li>• <strong>Override:</strong> Don't irrigate if rain detected</li>
                  <li>• <strong>Latency:</strong> &lt;1 second</li>
                </ul>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">Communication</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• WiFi/LoRaWAN connectivity</li>
                  <li>• MQTT protocol (lightweight)</li>
                  <li>• Publish aggregated data</li>
                  <li>• Deep sleep mode (power saving)</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-4 bg-green-100 border-l-4 border-green-600 p-4 rounded">
              <p className="text-sm font-semibold text-green-800">
                ⚡ Edge Benefit: Immediate irrigation decisions without waiting for cloud response. Operates even if internet connection is temporarily lost.
              </p>
            </div>
          </div>

          {/* Communication Layer */}
          <div className="flex justify-center">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-5 text-white shadow-lg max-w-2xl">
              <div className="flex items-center justify-center space-x-3 mb-2">
                <Wifi className="w-6 h-6" />
                <span className="font-bold text-lg">MQTT Protocol over TLS/SSL</span>
                <Wifi className="w-6 h-6" />
              </div>
              <p className="text-sm text-center">Secure, lightweight pub/sub messaging</p>
              <p className="text-xs text-center mt-1 opacity-90">Topic: farm/field_01/sensors | QoS: 1 (at least once delivery)</p>
            </div>
          </div>

          {/* Cloud Layer */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-600">
            <div className="flex items-center mb-4">
              <Cloud className="w-7 h-7 text-purple-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-800">3. Cloud Layer (GCP Infrastructure)</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-2">Compute Engine VM (IaaS)</h3>
                <p className="text-sm text-gray-700 mb-2">Ubuntu 22.04 on e2-micro instance</p>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• Docker containerized services</li>
                  <li>• EMQX MQTT Broker</li>
                  <li>• InfluxDB (time-series database)</li>
                  <li>• Telegraf (data ingestion)</li>
                </ul>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-2">External APIs (Integration)</h3>
                <p className="text-sm text-gray-700 mb-2">Weather data enrichment</p>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• OpenWeatherMap API (free tier)</li>
                  <li>• Fetch forecast: rain, temp, humidity</li>
                  <li>• Calculate evapotranspiration (ET)</li>
                  <li>• Optimize irrigation schedule</li>
                </ul>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-2">Data Storage</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• InfluxDB time-series DB</li>
                  <li>• 30-day retention policy</li>
                  <li>• Downsampling for long-term data</li>
                  <li>• ~10 MB/month per field</li>
                </ul>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-2">Analytics Engine</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Historical trend analysis</li>
                  <li>• Irrigation efficiency metrics</li>
                  <li>• Water savings calculation</li>
                  <li>• Crop growth correlation</li>
                </ul>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-2">Alert System</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Node.js notification service</li>
                  <li>• Email alerts (SMTP)</li>
                  <li>• SMS via Twilio (optional)</li>
                  <li>• Push notifications (future)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Application Layer */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center mb-4">
              <BarChart3 className="w-7 h-7 text-green-600 mr-3" />
              <h2 className="text-2xl font-bold text-gray-800">4. Application Layer (Farmer Interface)</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">📊 Web Dashboard</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Real-time soil moisture graphs</li>
                  <li>• Multi-field comparison view</li>
                  <li>• Weather forecast integration</li>
                  <li>• Irrigation recommendations</li>
                </ul>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">📈 Analytics Reports</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Water usage tracking</li>
                  <li>• Cost savings calculations</li>
                  <li>• Historical trends (weekly/monthly)</li>
                  <li>• Export to PDF/CSV</li>
                </ul>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">🔔 Notifications</h3>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Low moisture alerts</li>
                  <li>• Irrigation reminders</li>
                  <li>• Sensor offline warnings</li>
                  <li>• Rain detection updates</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Data Flow Visualization */}
          <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl p-6 text-white">
            <h2 className="text-xl font-bold mb-4 text-center">🔄 Complete Data Flow</h2>
            <div className="flex flex-wrap justify-center items-center gap-2 text-sm">
              <span className="bg-green-600 px-4 py-2 rounded-lg">Soil Sensor</span>
              <span className="text-2xl">→</span>
              <span className="bg-blue-600 px-4 py-2 rounded-lg">ESP32 Edge</span>
              <span className="text-2xl">→</span>
              <span className="bg-purple-600 px-4 py-2 rounded-lg">MQTT Publish</span>
              <span className="text-2xl">→</span>
              <span className="bg-purple-600 px-4 py-2 rounded-lg">Cloud Broker</span>
              <span className="text-2xl">→</span>
              <span className="bg-purple-600 px-4 py-2 rounded-lg">Telegraf</span>
              <span className="text-2xl">→</span>
              <span className="bg-purple-600 px-4 py-2 rounded-lg">InfluxDB</span>
              <span className="text-2xl">→</span>
              <span className="bg-yellow-600 px-4 py-2 rounded-lg">Weather API</span>
              <span className="text-2xl">→</span>
              <span className="bg-green-600 px-4 py-2 rounded-lg">Dashboard</span>
            </div>
            <p className="text-center text-sm mt-4 opacity-90">
              Reading frequency: Every 5 minutes | Data latency: &lt;10 seconds | Storage: 30 days detailed + 1 year downsampled
            </p>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4 border-t-4 border-green-500">
              <div className="text-3xl font-bold text-green-600 mb-1">40%</div>
              <div className="text-sm text-gray-600">Water Savings</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-t-4 border-blue-500">
              <div className="text-3xl font-bold text-blue-600 mb-1">$8/mo</div>
              <div className="text-sm text-gray-600">Cloud Costs</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-t-4 border-purple-500">
              <div className="text-3xl font-bold text-purple-600 mb-1">&lt;10s</div>
              <div className="text-sm text-gray-600">Data Latency</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-t-4 border-orange-500">
              <div className="text-3xl font-bold text-orange-600 mb-1">24/7</div>
              <div className="text-sm text-gray-600">Monitoring</div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}