-- Create Patients Table
CREATE TABLE Patient (
    patient_id INT NOT NULL PRIMARY KEY,
    phone CHAR(10),
    address CHAR(50),
    patient_name CHAR(50) NOT NULL,
    health JSON
);

-- Create Conversation_Template Table
CREATE TABLE Conversation_Template (
    convo_template_id INT NOT NULL PRIMARY KEY,
    convo_name CHAR(50),
    convo_workflow JSON,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Schedule Table
CREATE TABLE Schedule (
    schedule_id INT NOT NULL PRIMARY KEY,
    convo_template_id INT NOT NULL,
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    frequency DATETIME,
    FOREIGN KEY (convo_template_id) REFERENCES Conversation_Template(convo_template_id)
);

-- Create Calls Table
CREATE TABLE Call (
    call_id INT NOT NULL PRIMARY KEY,
    patient_id INT NOT NULL,
    convo_template_id INT NOT NULL,
    schedule_id INT NOT NULL,
    transcript JSON,
    audio CHAR(100), -- S3 Bucket reference
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),
    FOREIGN KEY (convo_template_id) REFERENCES Conversation_Template(convo_template_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id)
);

-- Insert data into Patients table
INSERT INTO Patient (patient_id, phone, address, patient_name, health) VALUES
(1, '1234567890', '123 Main St', 'John Doe', '{"allergies": "peanuts", "medication": "aspirin", "exercise_level": "moderate", "mental_health": "good", "social_health": "active", "emergency_contact": "Bob Doe"}'),
(2, '0987654321', '456 Elm St', 'Jane Smith', '{"allergies": "none", "medication": "ibuprofen", "exercise_level": "low", "mental_health": "fair", "social_health": "introverted", "emergency_contact": "Laurie Smith"}');

-- Insert data into Conversation_Template table
INSERT INTO Conversation_Template (convo_template_id, convo_name, convo_workflow, last_updated) VALUES
(1, 'New Patient', '{}', '2024-01-01 10:00:00'),
(2, 'Medical Checkup', '{}', '2024-01-01 10:00:00');

-- Insert data into Schedule table
INSERT INTO Schedule (schedule_id, convo_template_id, start_date, end_date, frequency) VALUES
(1, 1, '2023-01-01 10:00:00', '2024-01-01 11:00:00', '1D'),
(2, 2, '2023-02-01 10:00:00', '2024-02-01 11:00:00', '2W');

-- Insert data into Calls table
INSERT INTO Call (call_id, patient_id, convo_template_id, schedule_id, transcript, audio, last_updated) VALUES
(1, 1, 1, 1, '{}', 'audio1.mp3', '2024-01-01 10:00:00'),
(2, 2, 2, 2, '{}', 'audio2.mp3', '2024-02-01 10:00:00');
