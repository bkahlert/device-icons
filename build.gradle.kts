plugins {
    kotlin("jvm") version "1.9.0"
    kotlin("plugin.serialization") version "1.9.0"
    application
}

group = "com.bkahlert"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jmdns:jmdns:3.5.8") { because("mDNS / Bonjour testing") }
    implementation(platform("com.bkahlert.kommons:kommons-bom:2.8.0"))
    implementation("com.bkahlert.kommons:kommons-exec")
    implementation("com.bkahlert.kommons:kommons-time")
    implementation("com.bkahlert.kommons:kommons-uri")
    implementation("com.bkahlert.kommons:kommons-logging-core")
    implementation("com.bkahlert.kommons:kommons-logging-logback")
    implementation(platform("org.jetbrains.kotlinx:kotlinx-coroutines-bom:1.7.1"))
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core")
    implementation(platform("org.jetbrains.kotlinx:kotlinx-serialization-bom:1.5.1"))
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-core")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json")

    testImplementation(kotlin("test"))
    testImplementation(platform("io.kotest:kotest-bom:5.6.2"))
    testImplementation("io.kotest:kotest-common")
    testImplementation("io.kotest:kotest-assertions-core")
    testImplementation("io.kotest:kotest-assertions-json")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test")
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(11)
}

application {
    mainClass.set("MainKt")
}
