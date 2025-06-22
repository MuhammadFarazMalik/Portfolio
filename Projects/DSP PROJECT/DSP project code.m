clc; 
fprintf('--- Audio denoising ---\n\n');  
% Load the noisy audio signal  

fprintf('-> Step 1/5: Load audio:');  
[y, Fe] = audioread("Recording.wav");  
x=y(100000:end, 1);
Nx = length(y);  
fprintf(' OK\n');  

% Algorithm parameters  
apriori_SNR = 1;  
alpha = 0.05;      
beta1 = 0.5;  
beta2 = 1;  
lambda = 3;  

% STFT parameters  
NFFT = 1024;  
window_length = round(0.031 * Fe);  
window = hamming(window_length);  
window = window(:);  
overlap = floor(0.45 * window_length);  

% Signal parameters  
t_min = 0.3;    
t_max = 2.0;   

% Construct spectrogram   
fprintf('-> Step 2/5: Constructing spectrogram -');  
[S, F, T] = spectrogram(x + i .* eps, window, window_length - overlap, NFFT, Fe);  
[Nf, Nw] = size(S);  
fprintf(' OK\n');  

% Noisy spectrum extraction  
fprintf('-> Step 3/5: Extract noise spectrum -');  
t_index = find(T > t_min & T < t_max);  
mgntopwr = abs(S(:, t_index)).^2;  
noisyspec = mean(mgntopwr, 2);  
acrsallwndows = repmat(noisyspec, 1, Nw);  
fprintf(' OK\n');  

% Estimate SNR  
fprintf('-> Step 4/5: Estimate SNR -');  
absS = abs(S).^2;  
SNR_est = max((absS ./ acrsallwndows) - 1, 0);  
if apriori_SNR == 1  
    SNR_est = filter((1 - alpha), [1 - alpha], SNR_est);  
end    
fprintf(' OK\n');  

% Compute attenuation map  
fprintf('-> Step 5/5: Compute TF attenuation map -');  
an_lk = max((1 - lambda * ((1 ./ (SNR_est + 1)).^beta1)).^beta2, 0);  
STFT = an_lk .* S;  
fprintf(' OK\n');  

% Compute Inverse STFT   
fprintf('-> Computing Inverse STFT:');  
ind = mod((1:window_length) - 1, Nf) + 1;  
output_signal = zeros((Nw - 1) * overlap + window_length, 1);  

for indice = 1:Nw  
    left_index = ((indice - 1) * overlap);  
    index = left_index + [1:window_length];  
    temp_ifft = real(ifft(STFT(:, indice), NFFT));  
    output_signal(index) = output_signal(index) + temp_ifft(ind) .* window;  
end  
fprintf(' OK\n');  

% Normalize the output signal  
output_signal = output_signal / max(abs(output_signal)); % Normalize to [-1, 1]  

  

% Clip the output signal to prevent exceeding amplitude limits  
output_signal(output_signal > 1) = 1;   
output_signal(output_signal < -1) = -1;   

% Display temporal signals and spectrogram  
figure  
subplot(2,1,1);  
t_index = find(T > t_min & T < t_max);  
plot([1:length(x)] / Fe, x);  
xlabel('Time (s)');  
ylabel('Amplitude');  
hold on;  
noise_interval = floor([T(t_index(1)) * Fe:T(t_index(end)) * Fe]);  
plot(noise_interval / Fe, x(noise_interval), 'r');  
hold off;  
legend('Original signal', 'Vuvuzela Only');  
title('Original Sound');  

% Show denoised signal  
subplot(2,1,2);  
plot([1:length(output_signal)] / Fe, output_signal);  
xlabel('Time (s)');  
ylabel('Amplitude');  
title('Sound without Vuvuzela');  

% Show spectrogram of original sound  
t_epsilon = 0.001;  
figure  
S_one_sided = max(S(1:length(F) / 2, :), t_epsilon);   
pcolor(T, F(1:end/2), 10 * log10(abs(S_one_sided)));  
shading interp;  
colormap('hot');  
title('Spectrogram: Speech + noise');  
xlabel('Time (s)');  
ylabel('Frequency (Hz)');  

% Show spectrogram of denoised sound  
figure  
S_one_sided = max(STFT(1:length(F) / 2, :), t_epsilon);   
pcolor(T, F(1:end/2), 10 * log10(abs(S_one_sided)));  
shading interp;  
colormap('hot');  
title('Spectrogram: denoised');  
xlabel('Time (s)');  
ylabel('Frequency (Hz)');  

% Listen to results  
audiowrite('Recording_processed.wav', output_signal, Fe);  
fprintf('Finished! Denoised audio saved as "Recording_processed.m4a".\n');