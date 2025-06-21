# MADCHASE_Thesis

🎓 **Master's Thesis Project**  
**Title:** *A Web-Based Control System for Massive Distributed Channel Sounder Equipment Networks*  
**Author:** Stan Notaert  
**Institution:** NTNU  
**Year:** 2025

---

## 📚 Overview

This repository contains the full codebase for my master's thesis project. The system enables scalable, distributed **channel sounding measurements** using a network of Raspberry Pi devices connected to **nRF52833 DK boards**, all orchestrated through a central web server. 

Key features:
- Remote control of wireless measurement experiments
- Real-time data exchange via MQTT
- Role-based coordination (initiator/reflector/passive)
- UART and SPI communication with embedded devices
- Easy deployment on commodity hardware

---

## 📁 Repository Structure

```text
MADCHASE_Thesis/
├── server/           # Web server and MQTT messaging coordinator
├── raspberry_pi/     # MQTT client scripts for the Raspberry Pi nodes
├── iq_sampler/       # Firmware for nRF52833 using the nRF5 SDK (with Makefile)
